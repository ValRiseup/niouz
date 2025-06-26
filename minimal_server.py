#!/usr/bin/env python3

import os
import sys

# Test des imports de base
try:
    from flask import Flask, jsonify
    print("✅ Flask import successful")
except ImportError as e:
    print(f"❌ Flask import failed: {e}")
    sys.exit(1)

# Configuration ultra-simple
app = Flask(__name__)

@app.route('/')
def hello():
    return {
        "status": "success",
        "message": "Minimal server is working!",
        "python_version": sys.version,
        "port": os.environ.get('PORT', 'not set'),
        "pwd": os.getcwd(),
        "files": os.listdir('.')[:10]  # First 10 files
    }

@app.route('/health')
def health():
    return {"status": "healthy"}

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    host = '0.0.0.0'
    
    print(f"🚀 Starting minimal server on {host}:{port}")
    print(f"🚀 Python version: {sys.version}")
    print(f"🚀 Current directory: {os.getcwd()}")
    print(f"🚀 PORT env var: {os.environ.get('PORT', 'not set')}")
    
    try:
        app.run(host=host, port=port, debug=False)
    except Exception as e:
        print(f"❌ Server failed to start: {e}")
        sys.exit(1) 