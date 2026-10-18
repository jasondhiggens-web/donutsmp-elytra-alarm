# DonutSMP Elytra Alarm — Website prototype

A web-based version with browser notifications, price chart, target alerts, and purchase tracking.

## Test locally

Install Python 3 and run `python server.py` in this folder, then visit http://localhost:8000.

## Publish for friends

Host this folder on a Python-capable HTTPS host (e.g. Render as a Web Service). Start command: `python server.py`. The server uses the host-provided `PORT` environment variable. Share the HTTPS link. A static-only host will NOT work because `/api/price` is a Python backend.

## Important limitations

- The server attempts to read the public HTML price ticker from Donut.Auction. This is NOT confirmed to work live. If prices are populated using JavaScript, the app will show 'Price not verified'. A supported API or server-side browser checker would be required.
- Notifications work only while the website tab remains open and the browser permits notifications. Closed-browser push requires service worker, push subscriptions, and a hosted background worker; not included.
- Purchases and targets remain local to each browser. Verified price history is collected by the server and shared across visitors.
- Hosting is not provided by this ZIP; deployment is required to get a public URL.

## Market history

The running server collects verified prices every 60 seconds and stores the last 24 hours in SQLite. Both charts offer 1 hour and 24 hours and retain $5M price increments. Readings from before a visitor opened the page load from `/api/history`. History begins when this version starts collecting; unavailable earlier prices and server downtime cannot be backfilled.

The default database is `data/history.sqlite3`. For persistence across deployments, attach a persistent disk and set `HISTORY_DB` to a file on that disk (for example `/var/data/history.sqlite3`). The hosting service must stay running to collect prices while no browsers are open; sleeping services have gaps.
