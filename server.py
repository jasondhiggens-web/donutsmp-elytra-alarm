import json, os, re, time, urllib.request
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from html.parser import HTMLParser

ROOT=Path(__file__).resolve().parent
URL='https://donut.auction/item/c4c7f62a-d21a-4e94-b6a3-355a15349705'
class Parser(HTMLParser):
    def __init__(self): super().__init__(); self.stack=[]; self.capture=0; self.parts=[]; self.values=[]
    def handle_starttag(self,tag,attrs):
        cls=dict(attrs).get('class','').split(); inside=any(x[1] for x in self.stack)
        self.stack.append((tag,inside or 'price-ticker' in cls))
        if tag=='span' and 'sr-only' in cls and inside: self.capture=len(self.stack); self.parts=[]
    def handle_data(self,data):
        if self.capture:self.parts.append(data)
    def handle_endtag(self,tag):
        if self.capture==len(self.stack):self.values.append(''.join(self.parts).strip());self.capture=0
        if self.stack:self.stack.pop()
def price(raw):
    m=re.fullmatch(r'\$?\s*([\d,]+(?:\.\d+)?)\s*([KMBT]?)',raw.strip(),re.I)
    if not m:return None
    v=float(m.group(1).replace(',',''))*{'':1,'K':1e3,'M':1e6,'B':1e9,'T':1e12}[m.group(2).upper()]
    return round(v) if 0<v<1e13 else None
class Handler(SimpleHTTPRequestHandler):
    def __init__(self,*a,**kw):super().__init__(*a,directory=str(ROOT),**kw)
    def do_GET(self):
        if self.path.split('?')[0]!='/api/price':return super().do_GET()
        try:
            req=urllib.request.Request(URL,headers={'User-Agent':'Mozilla/5.0','Accept':'text/html'})
            with urllib.request.urlopen(req,timeout=20) as r: html=r.read(3000000).decode('utf-8','replace')
            parser=Parser();parser.feed(html)
            values=[price(v) for v in parser.values];values=[v for v in values if v is not None]
            if len(values)!=1:raise ValueError('The price is not present in the public HTML. The site may require JavaScript or a supported API.')
            payload={'verified':True,'price':values[0],'source':URL,'checked_at':int(time.time())}
        except Exception as e:payload={'verified':False,'error':str(e)[:240],'checked_at':int(time.time())}
        body=json.dumps(payload).encode();self.send_response(200);self.send_header('Content-Type','application/json');self.send_header('Cache-Control','no-store');self.send_header('Content-Length',str(len(body)));self.end_headers();self.wfile.write(body)
if __name__=='__main__':
    port=int(os.environ.get('PORT','8000'));print(f'Open http://localhost:{port}',flush=True)
    ThreadingHTTPServer(('0.0.0.0',port),Handler).serve_forever()
