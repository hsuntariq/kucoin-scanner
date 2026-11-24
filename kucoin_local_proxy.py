#!/usr/bin/env python3
"""Minimal local CORS proxy for the KuCoin RSI dashboard."""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.request import Request, urlopen
from urllib.error import HTTPError

BASE = "https://api.kucoin.com"

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
        if not self.path.startswith("/api/v1/"):
            self.send_headers(404)
            self.wfile.write(b'{"error":"Not found"}')
            return
        try:
            req = Request(BASE + self.path, headers={"User-Agent": "Crypto-RSI-local-proxy"})
            with urlopen(req, timeout=15) as response:
                self.send_headers(response.status, response.headers.get("Content-Type", "application/json"))
                self.wfile.write(response.read())
        except HTTPError as e:
            self.send_headers(e.code)
            self.wfile.write(e.read())
        except Exception as e:
            self.send_headers(502)
            self.wfile.write(('{"error":"Proxy error: ' + str(e).replace('"', '\\"') + '"}').encode())

    def log_message(self, fmt, *args):
        print(fmt % args)

if __name__ == "__main__":
    print("KuCoin proxy running at http://127.0.0.1:8787 — keep this window open.")
    ThreadingHTTPServer(("127.0.0.1", 8787), Handler).serve_forever()
