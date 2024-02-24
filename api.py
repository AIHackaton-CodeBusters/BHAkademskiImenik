from flask import Flask, jsonify, request
import requests

app = Flask(__name__)

@app.route('/summarize/<paper_id>')
def summarize(paper_id):
    response = getPaperSummary(paper_id)

    if response.status_code == 200:
        summary = response.json()
        return jsonify({'summary': summary})
    else:
        return jsonify({'error': f"Request failed with status code {response.status_code}: {response.text}"}), response.status_code

if __name__ == '__main__':
    app.run(debug=True, port=3000)


