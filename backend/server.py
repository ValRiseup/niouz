from flask import Flask, Response
import subprocess
import sys
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/refresh-data', methods=['GET'])
def refresh_data():
    def generate():
        python_executable = sys.executable
        script_dir = os.path.dirname(os.path.abspath(__file__))
        scraper_path = os.path.join(script_dir, 'scraper.py')
        
        process = subprocess.Popen(
            [python_executable, scraper_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )

        for line in iter(process.stdout.readline, ''):
            yield f"data: {line}\n\n"

        process.stdout.close()
        return_code = process.wait()

        if return_code != 0:
            error_output = process.stderr.read()
            yield f"data: ERROR: {error_output}\n\n"

        yield "data: DONE\n\n"

    return Response(generate(), mimetype='text/event-stream')

if __name__ == '__main__':
    app.run(debug=True, port=5001) 