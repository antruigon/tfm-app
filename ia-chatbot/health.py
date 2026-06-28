import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

from config import HEALTH_PORT


class _HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/health":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"status":"ok"}')
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, _format, *_args):
        return


def start_health_server() -> None:
    server = HTTPServer(("0.0.0.0", HEALTH_PORT), _HealthHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
