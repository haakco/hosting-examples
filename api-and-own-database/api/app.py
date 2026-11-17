"""A minimal API: GET /up reports whether the database named by DATABASE_URL answers."""

import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import psycopg


def database_report() -> dict:
    with psycopg.connect(os.environ["DATABASE_URL"], connect_timeout=3) as connection:
        version = connection.execute("SELECT current_setting('server_version')").fetchone()[0]
    return {"database": "ok", "serverVersion": version}


class Handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        if self.path != "/up":
            self.respond(404, {"error": "not found"})
            return
        try:
            self.respond(200, database_report())
        except (psycopg.Error, KeyError) as error:
            self.respond(503, {"database": "unreachable", "reason": type(error).__name__})

    def respond(self, status: int, body: dict) -> None:
        payload = json.dumps(body).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)


if __name__ == "__main__":
    ThreadingHTTPServer(("0.0.0.0", int(os.environ.get("PORT", "8080"))), Handler).serve_forever()
