
#!/usr/bin/env python3
"""KuCoin RSI Dashboard - Local and Render-compatible server."""

import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from pathlib import Path

BASE = "https://api.kucoin.com"
PORT = int(os.environ.get("PORT", 8787))
HOST = "0.0.0.0"
DASHBOARD = Path(__file__).parent / "main.html"


class Handler(BaseHTTPRequestHandler):

    def send_headers(self, status=200, content_type="application/json"):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()

    def do_OPTIONS(self):
        self.send_headers(204)

    def do_GET(self):

        # Serve dashboard
        if self.path == "/" or self.path.startswith("/main.html"):
            try:
                content = DASHBOARD.read_bytes()
                self.send_headers(200, "text/html; charset=utf-8")
                self.wfile.write(content)
            except FileNotFoundError:
                self.send_headers(404, "text/plain")
                self.wfile.write(b"main.html not found")
            return

        # Proxy KuCoin API
        if not self.path.startswith("/api/v1/"):
            self.send_headers(404)
            self.wfile.write(b'{"error":"Not found"}')
            return

        try:
            req = Request(
                BASE + self.path,
                headers={"User-Agent": "Crypto-RSI-Dashboard"}
            )

            with urlopen(req, timeout=15) as response:
                self.send_headers(
                    response.status,
                    response.headers.get("Content-Type", "application/json")
                )
                self.wfile.write(response.read())

        except HTTPError as e:
            self.send_headers(e.code)
            self.wfile.write(e.read())

        except Exception as e:
            self.send_headers(502)
            error = str(e).replace('"', '\\"')
            self.wfile.write(
                ('{"error":"Proxy error: ' + error + '"}').encode()
            )

    def log_message(self, fmt, *args):
        print(fmt % args)


if __name__ == "__main__":
    print(f"KuCoin dashboard server running on port {PORT}")
    ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()
