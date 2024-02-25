import csv
from http import client
from openai import OpenAI
import requests
import fitz  
import json
import requests
from flask import Flask, jsonify, request

app = Flask(__name__)

csv_file = "data/publications.csv"

# Replace 'YOUR_API_KEY' with your actual OpenAI API key
api_key = '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'
client = OpenAI(api_key=api_key)

# Server URL, change server_url string with one provided
# Access this link at the beginning with the password provided through any browser
server_url = "https://late-wasps-joke.loca.lt"
completions_endpoint = server_url + "/v1/completions"

# Function to get paper summary
def getPaperSummary(paper_id):
    # Read PDF link for the provided paper_id
    pdf_link = read_pdf_link_from_csv(csv_file, paper_id)
    if pdf_link:
        # Fetch paper content from the PDF link
        response = requests.get(pdf_link)
        pdf_bytes = response.content
        pdf_document = fitz.open("pdf", pdf_bytes)
        pdf_text = ""
        
        # Iterate through each page and extract text
        for page_number in range(pdf_document.page_count):
            page = pdf_document[page_number]
            pdf_text += page.get_text()

        # Close the PDF document
        pdf_document.close()

        completion = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are requested to simplify a document."},
                    {"role": "user", "content": "Simplify the document and include headings to make it understandable for people with limited knowledge on the subject."},
                    {"role": "user", "content": "The document should be no longer than 2 pages."},
                    {"role": "user", "content": "Here is the text: " + pdf_text}  # Providing the extracted text from the PDF
                ]
        )
        # Accessing the first message in the completion
        response_message = completion.choices[0].message
        summary = response_message.content
        return summary
    else:
        return f"Paper ID '{paper_id}' not found."


# Function to read PDF link from the CSV file
def read_pdf_link_from_csv(csv_file, paper_id):
    with open(csv_file, 'r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            semantic_paper_id = row.get('SemanticPaperId')
            pdf_info = row.get('openAccessPdf')
            if semantic_paper_id == paper_id and pdf_info:
                try:
                    pdf_info_dict = json.loads(pdf_info)
                    pdf_url = pdf_info_dict.get('url')
                    if pdf_url:
                        return pdf_url
                except json.JSONDecodeError:
                    print(f"Error decoding JSON: {pdf_info}")
    return None

def translateDocument(paper_summary, target_language):
    # Define payload for translation request
    translation_payload = {
        "model": "mistralai/Mistral-7B-Instruct-v0.2",
        "prompt": f"TASK: Translate the following text in {target_language}. Use all the sentences.\n\n Text:{paper_summary}&&",
        "stop": "&&",
        "max_tokens": 1500,
        "temperature": 0
    }
    
    # Send translation request
    response = requests.post(completions_endpoint, json=translation_payload)
    
    # Check response status
    if response.status_code == 200:
        # Extract translated text
        translated_text = response.json()['choices'][0]['text']
        return translated_text
    else:
        return None

@app.route('/simplifyOtherLanguages/<paper_id>', methods=['GET'])
def simplifyOtherLanguages(paper_id):
    target_language = request.args.get('target_language')
    if target_language:
        summary = getPaperSummary(paper_id)
        if summary:
            translated_summary = translateDocument(summary, target_language)
            print(translated_summary)
            if translated_summary:
                return jsonify({'summary': translated_summary})
            else:
                return jsonify({'error': 'Failed to translate the document'}), 500
        else:
            return jsonify({'error': 'Failed to retrieve paper summary'}), 404
    else:
        return jsonify({'error': 'Target language not provided in the request'}), 400


@app.route('/simplifyEN/<paper_id>', methods=['GET'])
def simplifyEN(paper_id):
    summary = getPaperSummary(paper_id)
    if summary:
        translated_summary = translateDocument(summary, 'English') 
        if translated_summary:
            return jsonify({'summary': translated_summary})
        else:
            return jsonify({'error': 'Failed to translate the document'}), 500
    else:
        return jsonify({'error': 'Paper not found'}), 404
    
if __name__ == '__main__':
    app.run(debug=True, port=3000)
