#!/usr/bin/env python

import os
from http.server import HTTPServer, BaseHTTPRequestHandler

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        
        message = f"""
        <html>
        <body>
            <h1>🎉 Railway Python SUCCESS!</h1>
            <p>Server is running on Railway!</p>
            <p>Port from env: {os.environ.get('PORT', 'not set')}</p>
        </body>
        </html>
        """
        
        self.wfile.write(message.encode())

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    server = HTTPServer(('0.0.0.0', port), Handler)
    print(f"Starting server on port {port}")
    server.serve_forever() 