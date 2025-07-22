import os
from http.server import BaseHTTPRequestHandler

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # This will run your tgfs bot
        os.system("python3 -m tgfs")
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"tgfs bot triggered (may stop after timeout)")
        return