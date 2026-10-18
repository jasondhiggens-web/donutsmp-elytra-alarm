# DonutSMP Elytra Alarm — Website prototype

A web-based version with browser notifications, price chart, target alerts, and purchase tracking.

## Test locally

Install Python 3 and run `python server.py` in this folder, then visit http://localhost:8000.

## Publish for friends

Host this folder on a Python-capable HTTPS host (e.g. Render as a Web Service). Start command: `python server.py`. The server uses the host-provided `PORT` environment variable. Share the HTTPS link. A static-only host will NOT work because `/api/price` is a Python backend.

## Important limitations

- The server attempts to read the public HTML price ticker from Donut.Auction. This is NOT confirmed to work live. If prices are populated using JavaScript, the app will show 'Price not verified'. A supported API or server-side browser checker would be required.
- Notifications work only while the website tab remains open and the browser permits notifications. Closed-browser push requires service worker, push subscriptions, and a hosted background worker; not included.
- Purchases, targets, and chart history are stored locally in each friend's browser, not synchronized across users.
- Hosting is not provided by this ZIP; deployment is required to get a public URL.
