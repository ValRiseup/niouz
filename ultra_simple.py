#!/usr/bin/env python

import http.server
import socketserver
import os

PORT = int(os.environ.get('PORT', 8000))

class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            response = '''
            <html>
            <body>
                <h1>🎉 Python Server Works!</h1>
                <p>Port: %s</p>
                <p>Path: %s</p>
                <p>Success! Railway can run Python!</p>
            </body>
            </html>
            ''' % (PORT, self.path)
            self.wfile.write(response.encode())
        else:
            super().do_GET()

with socketserver.TCPServer(("0.0.0.0", PORT), Handler) as httpd:
    print(f"Server running on port {PORT}")
    httpd.serve_forever() 