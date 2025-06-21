import http.server
import socketserver

PORT = 8000

class HandlerWithHeaders(http.server.SimpleHTTPRequestHandler):
    class HandlerWithHeaders(http.server.SimpleHTTPRequestHandler):
        def end_headers(self):

            super().end_headers()


with socketserver.TCPServer(("0.0.0.0", PORT), HandlerWithHeaders) as httpd:
    print(f"Serving at http://localhost:{PORT}")
    httpd.serve_forever()

