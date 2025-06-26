from flask import Flask, Response, request
import subprocess
import sys
import os
from flask_cors import CORS
import signal

app = Flask(__name__)
CORS(app)

# Timeout handler for long-running processes
class TimeoutError(Exception):
    pass

def timeout_handler(signum, frame):
    raise TimeoutError("Operation timed out")

@app.route('/', methods=['GET'])
def health_check():
    return {
        "status": "healthy",
        "message": "AI News Backend is running",
        "version": "1.0.0"
    }

@app.route('/refresh-data', methods=['GET'])
def refresh_data():
    # Extract mode parameter outside the generator function
    mode = request.args.get('mode', 'normal')
    
    def generate():
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            # Use system python in production, venv python in development
            python_executable = 'python' if os.environ.get('RAILWAY_ENVIRONMENT') else os.path.join(script_dir, 'venv/bin/python')
            scraper_path = os.path.join(script_dir, 'scraper.py')
            
            # Build command based on mode parameter
            command = [python_executable, scraper_path]
            
            if mode == 'all':
                command.append('--all')
                print("🚀 [SERVER] Starting scraper with --all mode", flush=True)
            elif mode == 'reset':
                command.append('--reset-timestamp')
                print("🚀 [SERVER] Starting scraper with --reset-timestamp mode", flush=True)
            else:
                print("🚀 [SERVER] Starting scraper in normal mode", flush=True)
            
            # Set up timeout for the process
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )

            # Read output with timeout protection
            line_count = 0
            for line in iter(process.stdout.readline, ''):
                yield f"data: {line}\n\n"
                line_count += 1
                
                # Send periodic heartbeats to prevent timeout
                if line_count % 10 == 0:
                    yield f"data: [HEARTBEAT] Processing... ({line_count} messages)\n\n"

            process.stdout.close()
            return_code = process.wait()

            if return_code != 0:
                error_output = process.stderr.read()
                print("--- SCRAPER ERROR ---", file=sys.stderr)
                print(error_output, file=sys.stderr)
                yield f"data: ERROR: {error_output}\n\n"

            yield "data: DONE\n\n"
            
        except Exception as e:
            print(f"[SERVER] Critical error in refresh_data: {e}", file=sys.stderr)
            yield f"data: ERROR: Server error - {str(e)}\n\n"

    return Response(generate(), mimetype='text/event-stream')

if __name__ == '__main__':
    # Production configuration
    port = int(os.environ.get('PORT', 5001))
    host = '0.0.0.0' if os.environ.get('RAILWAY_ENVIRONMENT') else '127.0.0.1'
    debug = not bool(os.environ.get('RAILWAY_ENVIRONMENT'))
    
    print(f"🚀 [SERVER] Starting server on {host}:{port} (debug={debug})")
    print(f"🚀 [SERVER] Environment: {'Production' if os.environ.get('RAILWAY_ENVIRONMENT') else 'Development'}")
    
    # Check critical environment variables
    if os.environ.get('RAILWAY_ENVIRONMENT'):
        if not os.environ.get('GEMINI_API_KEY'):
            print("⚠️  [SERVER] WARNING: GEMINI_API_KEY not set in production!")
        else:
            print("✅ [SERVER] GEMINI_API_KEY is configured")
    
    app.run(debug=debug, host=host, port=port, threaded=True) 