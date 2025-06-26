#!/usr/bin/env python3

import http.server
import socketserver
import os
import json
from urllib.parse import urlparse

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            response = {
                "status": "success",
                "message": "Simple HTTP server working!",
                "port": os.environ.get('PORT', 'not set'),
                "path": self.path,
                "server": "Python http.server"
            }
            
            self.wfile.write(json.dumps(response).encode())
        elif self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"status": "healthy"}')
        else:
            self.send_response(404)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"error": "Not found"}')

if __name__ == "__main__":
    PORT = int(os.environ.get('PORT', 5001))
    HOST = '0.0.0.0'
    
    print(f"🚀 Starting simple HTTP server on {HOST}:{PORT}")
    print(f"🚀 PORT env var: {os.environ.get('PORT', 'not set')}")
    print(f"🚀 Current directory: {os.getcwd()}")
    
    with socketserver.TCPServer((HOST, PORT), MyHTTPRequestHandler) as httpd:
        print(f"✅ Server running at http://{HOST}:{PORT}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 Server stopped")
        except Exception as e:
            print(f"❌ Server error: {e}") 