from flask import Flask, Response, request, jsonify
import subprocess
import sys
import os
import json
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/', methods=['GET'])
def health_check():
    return {
        "status": "healthy",
        "message": "AI News Backend is running (Fallback Mode)",
        "version": "1.0.0-fallback",
        "database": "JSON file mode"
    }

@app.route('/api/news-data', methods=['GET'])
def get_news_data():
    """Get combined articles and topics data from JSON file (fallback)"""
    try:
        # Try to load from JSON file
        script_dir = os.path.dirname(os.path.abspath(__file__))
        data_path = os.path.join(script_dir, '../src/data.js')
        
        if os.path.exists(data_path):
            with open(data_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # Extract JSON from "export const newsData = {...};"
                json_start = content.find('{')
                json_end = content.rfind('}') + 1
                json_str = content[json_start:json_end]
                data = json.loads(json_str)
        else:
            data = {"articles": [], "topics": []}
        
        return jsonify({
            "success": True,
            "data": data,
            "meta": {
                "articles_count": len(data.get('articles', [])),
                "topics_count": len(data.get('topics', [])),
                "source": "JSON file fallback",
                "last_updated": None
            }
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Fallback error: {str(e)}",
            "data": {"articles": [], "topics": []}
        }), 200  # Return 200 to avoid breaking frontend

@app.route('/refresh-data', methods=['GET'])
def refresh_data():
    """Simplified refresh without database"""
    def generate():
        yield f"data: Starting fallback refresh...\n\n"
        yield f"data: Database mode not available in fallback\n\n"
        yield f"data: Using existing JSON data\n\n"
        yield f"data: DONE\n\n"
    
    return Response(generate(), mimetype='text/event-stream')

if __name__ == '__main__':
    # Production configuration
    port = int(os.environ.get('PORT', 5001))
    host = '0.0.0.0'
    debug = False
    
    print(f"🚀 [FALLBACK] Starting fallback server on {host}:{port}")
    print(f"🚀 [FALLBACK] Environment: Production Fallback Mode")
    print(f"🚀 [FALLBACK] Using JSON file instead of database")
    
    app.run(debug=debug, host=host, port=port, threaded=True) 