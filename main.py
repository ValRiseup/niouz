#!/usr/bin/env python

import http.server
import socketserver
import os

PORT = int(os.environ.get('PORT', 8000))

class MyHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        html = f"""
        <h1>✅ SUCCESS! Railway + Python Working!</h1>
        <p><strong>Port:</strong> {PORT}</p>
        <p><strong>Path:</strong> {self.path}</p>
        <p><strong>Status:</strong> Railway successfully detected and ran Python!</p>
        <p>Now we can deploy the real backend with database! 🚀</p>
        """
        self.wfile.write(html.encode())

with socketserver.TCPServer(("0.0.0.0", PORT), MyHandler) as httpd:
    print(f"✅ Server started on port {PORT}")
    httpd.serve_forever() 