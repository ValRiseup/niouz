#!/usr/bin/env python

import http.server
import socketserver
import os

# Railway port parsing with error handling
try:
    PORT = int(os.environ.get('PORT', '8000'))
    if not (0 <= PORT <= 65535):
        raise ValueError(f"Invalid port: {PORT}")
except (ValueError, TypeError) as e:
    print(f"❌ Port error: {e}")
    print(f"PORT env var: '{os.environ.get('PORT', 'not set')}'")
    PORT = 8000

class MyHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        html = f"""
        <h1>✅ SUCCESS! Railway + Python Working!</h1>
        <p><strong>Port:</strong> {PORT}</p>
        <p><strong>Port ENV:</strong> {os.environ.get('PORT', 'not set')}</p>
        <p><strong>Path:</strong> {self.path}</p>
        <p><strong>Status:</strong> Railway successfully detected and ran Python!</p>
        <p>🎉 Port parsing issue SOLVED! Now we can deploy the real backend with database! 🚀</p>
        """
        self.wfile.write(html.encode())

print(f"🚀 Starting server...")
print(f"🚀 PORT env variable: '{os.environ.get('PORT', 'not set')}'")
print(f"🚀 Parsed PORT: {PORT}")
print(f"🚀 Port type: {type(PORT)}")

with socketserver.TCPServer(("0.0.0.0", PORT), MyHandler) as httpd:
    print(f"✅ Server successfully started on 0.0.0.0:{PORT}")
    httpd.serve_forever() 