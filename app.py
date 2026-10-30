#!/usr/bin/env python3
"""Serves the built site (dist/index.html).

Start command:  python app.py
Port:           reads $PORT (default 8080). Health check: /healthz
If dist/index.html does not exist yet, it is built first (needs: pip install -r requirements.txt).
"""
import gzip
import os
import subprocess
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

BASE = os.path.dirname(os.path.abspath(__file__))
INDEX_PATH = os.path.join(BASE, "dist", "index.html")

if not os.path.exists(INDEX_PATH):
    print("dist/index.html not found, building...", flush=True)
    subprocess.check_call([sys.executable, os.path.join(BASE, "build.py"), "--local"], cwd=BASE)

with open(INDEX_PATH, "rb") as f:
    INDEX = f.read()
INDEX_GZ = gzip.compress(INDEX, 6)


class Handler(BaseHTTPRequestHandler):
    server_version = "AzureSOPKB"

    def _send(self, status, body, ctype, head=False, gz=False):
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        if gz:
            self.send_header("Content-Encoding", "gzip")
        self.send_header("Vary", "Accept-Encoding")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "SAMEORIGIN")
        self.send_header("Referrer-Policy", "strict-origin-when-cross-origin")
        self.end_headers()
        if not head:
            self.wfile.write(body)

    def _handle(self, head):
        path = self.path.split("?", 1)[0].split("#", 1)[0]
        if path == "/healthz":
            return self._send(200, b"ok", "text/plain; charset=utf-8", head)
        use_gz = "gzip" in self.headers.get("Accept-Encoding", "")
        body = INDEX_GZ if use_gz else INDEX
        self._send(200, body, "text/html; charset=utf-8", head, gz=use_gz)

    def do_GET(self):
        self._handle(False)

    def do_HEAD(self):
        self._handle(True)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8080"))
    print(f"Serving on 0.0.0.0:{port}", flush=True)
    ThreadingHTTPServer(("0.0.0.0", port), Handler).serve_forever()
