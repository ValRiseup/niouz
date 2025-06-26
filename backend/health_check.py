#!/usr/bin/env python3
"""
Simple health check script to test Railway deployment
"""

import os
import sys

def main():
    print("🔍 [HEALTH] Starting health check...")
    
    # Check Python version
    print(f"🐍 [HEALTH] Python version: {sys.version}")
    
    # Check environment
    env = "Production" if os.environ.get('RAILWAY_ENVIRONMENT') else "Development"
    print(f"🌍 [HEALTH] Environment: {env}")
    
    # Check critical environment variables
    gemini_key = os.environ.get('GEMINI_API_KEY')
    if gemini_key:
        print(f"✅ [HEALTH] GEMINI_API_KEY: Set (length: {len(gemini_key)})")
    else:
        print("❌ [HEALTH] GEMINI_API_KEY: Missing!")
    
    # Check port
    port = os.environ.get('PORT', '5001')
    print(f"🚪 [HEALTH] Port: {port}")
    
    # Check if we can import required modules
    try:
        import flask
        print(f"✅ [HEALTH] Flask: {flask.__version__}")
    except ImportError as e:
        print(f"❌ [HEALTH] Flask import error: {e}")
    
    try:
        import google.generativeai as genai
        print("✅ [HEALTH] Google AI SDK: Available")
    except ImportError as e:
        print(f"❌ [HEALTH] Google AI SDK error: {e}")
    
    try:
        import feedparser
        print("✅ [HEALTH] Feedparser: Available")
    except ImportError as e:
        print(f"❌ [HEALTH] Feedparser error: {e}")
    
    # Check current directory and files
    current_dir = os.getcwd()
    print(f"📁 [HEALTH] Current directory: {current_dir}")
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"📁 [HEALTH] Script directory: {script_dir}")
    
    # Check if critical files exist
    critical_files = ['server.py', 'scraper.py', 'cron_scraper.py']
    for file in critical_files:
        file_path = os.path.join(script_dir, file)
        if os.path.exists(file_path):
            print(f"✅ [HEALTH] File exists: {file}")
        else:
            print(f"❌ [HEALTH] File missing: {file}")
    
    print("🏁 [HEALTH] Health check completed!")

if __name__ == "__main__":
    main() 