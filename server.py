"""DonutSMP Elytra Alarm backend: browser-rendered price verification.

Only publishes a price when exactly one valid ticker value was found.
"""
import json
import os
import re
import threading
import time
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent
URL = 'https://donut.auction/item/c4c7f62a-d21a-4e94-b6a3-355a15349705'
SELECTOR = '.price-ticker span.sr-only'
CACHE_SECONDS = 55
_lock = threading.Lock()
_cached = None
_cached_until = 0


def parse_price(raw):
    match = re.fullmatch(r'\$?\s*([\d,]+(?:\.\d+)?)\s*([KMBT]?)', raw.strip(), re.I)
    if not match:
        return None
    value = float(match.group(1).replace(',', '')) * {
        '': 1, 'K': 1e3, 'M': 1e6, 'B': 1e9, 'T': 1e12
    }[match.group(2).upper()]
    return round(value) if 0 < value < 1e13 else None


def retrieve_price():
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        # Chromium runs on Render, not on your friends' computers.
        browser = p.chromium.launch(headless=True, args=['--no-sandbox', '--disable-dev-shm-usage'])
        try:
            page = browser.new_page(viewport={'width': 1280, 'height': 800})
            page.goto(URL, wait_until='domcontentloaded', timeout=35000)
            page.locator(SELECTOR).first.wait_for(state='attached', timeout=20000)
            # Allow a moment for dynamically populated ticker values.
            page.wait_for_timeout(1000)
            strings = page.locator(SELECTOR).all_text_contents()
            values = [parse_price(s) for s in strings]
            values = [v for v in values if v is not None]
            if len(values) != 1:
                raise ValueError(f'Expected one valid live price; found {len(values)}. The site layout may have changed.')
            return values[0]
        finally:
            browser.close()


def price_payload():
    global _cached, _cached_until
    with _lock:
        now = time.time()
        if _cached is not None and now < _cached_until:
            return _cached
        try:
            value = retrieve_price()
            result = {'verified': True, 'price': value, 'source': URL, 'checked_at': int(time.time())}
            _cached_until = time.time() + CACHE_SECONDS
        except Exception as exc:
            result = {'verified': False, 'error': f'{type(exc).__name__}: {str(exc)[:190]}', 'checked_at': int(time.time())}
            _cached_until = time.time() + 15
        _cached = result
        return result


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def do_GET(self):
        if self.path.split('?', 1)[0] != '/api/price':
            return super().do_GET()
        body = json.dumps(price_payload()).encode('utf-8')
        self.send_response(200)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Cache-Control', 'no-store')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        try:
            self.wfile.write(body)
        except (BrokenPipeError, ConnectionResetError):
            pass


if __name__ == '__main__':
    port = int(os.environ.get('PORT', '8000'))
    print(f'Listening on port {port}', flush=True)
    ThreadingHTTPServer(('0.0.0.0', port), Handler).serve_forever()
