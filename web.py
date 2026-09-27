from http.server import HTTPServer, BaseHTTPRequestHandler
import os

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot Highrise actif !")

def run():
    port = int(os.environ.get("PORT", 10000))
    server_address = ('', port)
    httpd = HTTPServer(server_address, SimpleHTTPRequestHandler)
    print(f"Serveur Web en écoute sur le port {port}...")
    httpd.serve_forever()

if __name__ == "__main__":
    run()
