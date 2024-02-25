from flask import Flask, jsonify, request
from readPublicationsCsv import getPublications
import requests

app = Flask(__name__)

@app.route('/search', methods=['GET'])
def search():
    # Define the API endpoint URL
    url = 'https://api.semanticscholar.org/graph/v1/paper/search'

    # More specific query parameter
    query = request.args.get('query')

    # Directly define the API key (Reminder: Securely handle API keys in production environments)
    api_key = 'NmKaEcYLf3N5DojI0Ajv26dc804QvjV4BwtLdFv1'  # Replace with the actual API key

    # Define headers with API key
    headers = {'x-api-key': api_key}

    # Send the API request
    response = requests.get(url, params={'query': query}, headers=headers)

    # Check response status
    if response.status_code == 200:
        response_data = response.json()
        return jsonify(response_data)
    else:
        return jsonify({'error': f"Request failed with status code {response.status_code}: {response.text}"}), response.status_code

@app.route('/suggested', methods = ['POST'])
def getSuggested():
    '''
    url = f'https://api.semanticscholar.org/recommendations/v1/papers/forpaper/{publicationId}?fields=authors,title'

    response = requests.get(url)
    
    if response.status_code != 200:
        return jsonify({'error': f"Request failed with status code {response.status_code}: {response.text}"}), response.status_code
    
    '''

    fieldsOfStudy = request.json['fieldsOfStudy']

    csvPublications = getPublications()

    publications = [csvPublication for csvPublication in csvPublications if any(fieldOfStudy == csvPublication.category for fieldOfStudy in fieldsOfStudy)]

    return jsonify([publication.to_dict() for publication in publications])


if __name__ == '__main__':
    app.run(debug=True)
