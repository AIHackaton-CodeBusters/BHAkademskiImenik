import csv
from http import client
from openai import OpenAI
import requests
import fitz  
import json
import httpx
import requests
from flask import Flask, jsonify, request
from collections import Counter
import re
from flask_cors import CORS

from readPublicationsCvs import Publication, getPublications

app = Flask(__name__)
CORS(app)
CORS(app, resources={r"/api/*": {"origins": "http://localhost:4200"}})
csv_file = "data/publications.csv"

# Server URL, change server_url string with one provided
# Access this link at the beginning with the password provided through any browser
server_url = "https://late-wasps-joke.loca.lt"
completions_endpoint = server_url + "/v1/completions"

# Function to get paper summary
async def getPaperSummary(paper_id):
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
        final_output = filterText(pdf_text)
        print("final_output")
        print(final_output)
        summary = await sendFilterTextToLLM(final_output)
        return summary
    else:
        return f"Paper ID '{paper_id}' not found."

async def sendFilterTextToLLM(final_output):
    payload = {
        "model": "mistralai/Mistral-7B-Instruct-v0.2",
        "prompt": " TASK: Rewrite the following scientific text in one paragraph for a non-educated human.\n\n Text:\n\n {}".format(final_output),
        "stop": "..",
        "max_tokens": 1500,
        "temperature": 0
    }
    async with httpx.AsyncClient() as client:
        # Make the API request
        response = requests.post(completions_endpoint, json=payload)
        # Check the response
        if response.status_code == 200:
            # Extract and print the text after the colon in 'text' attribute
            api_response_text = response.json()['choices'][0]['text']
            extracted_text = api_response_text.split(':', 1)[-1].strip()
            return extracted_text
        else:
            # Print an error message if the request was not successful
            print(f"Error: {response.status_code}, {response.text}")


def filterText(pdf_text):
    # Replace '-\n' with ''
    modified_text1 = pdf_text.replace('-\n', '')
    # Replace '\n' with ' '
    modified_text = modified_text1.replace('\n', ' ')
    # Find the top 5 most used words with more than 6 characters
    words = re.findall(r'\b\w{7,}\b', modified_text.lower())
    top_5_words = [word for word, _ in Counter(words).most_common(5)]
    # List of words to exclude sentences
    exclusion_words = ['exclude_word1', 'exclude_word2', 'exclude_word3']
    # Initialize variables for total token count and limit
    total_tokens = 0
    limit = 750
    # Initialize an empty list to store sentences containing top 5 words
    sentences_with_top_words = []
    # Split the text into sentences
    sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', modified_text)
    # Check if a sentence contains at least one of the top 5 words, no digits, less than 3 commas, and not containing exclusion words
    for sentence in sentences:
        sentence = sentence.replace('\n', ' ')  # Replace newline characters with spaces
        if (
            any(word in sentence.lower() for word in top_5_words)
            and not any(char.isdigit() for char in sentence)
            and sentence.count(',') <= 3
            and not any(ex_word in sentence.lower() for ex_word in exclusion_words)
        ):
            sentence_tokens = len(re.findall(r'\b\w+\b', sentence))
            if total_tokens + sentence_tokens <= limit:
                sentences_with_top_words.append(sentence)
                total_tokens += sentence_tokens
            else:
                break  # Break the loop if the limit is reached
    # Combine sentences into a single paragraph
    final_output = ' '.join(sentences_with_top_words) ## FINAL OUTPUT JE TEXT KOJI SALJEMO LLM-u!!!!!!
    return final_output

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

async def translateDocument(paper_summary, target_language):
    # Define payload for translation request
    print("DOBIO PARAMETAR")
    print(paper_summary)

    translation_payload = {
        "model": "mistralai/Mistral-7B-Instruct-v0.2",
        "prompt": f"TASK: Translate the following text in {target_language}. Use all the sentences.\n\n Text:{paper_summary}&&",
        "stop": "&&",
        "max_tokens": 1500,
        "temperature": 0
    }
    
    # Send translation request asynchronously
    async with httpx.AsyncClient() as client:
        response = await client.post(completions_endpoint, json=translation_payload)
    
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
            if translated_summary:
                return jsonify({'summary': translated_summary})
            else:
                return jsonify({'error': 'Failed to translate the document'}), 500
        else:
            return jsonify({'error': 'Failed to retrieve paper summary'}), 404
    else:
        return jsonify({'error': 'Target language not provided in the request'}), 400


@app.route('/simplify/<paper_id>', methods=['GET'])
async def simplifyEN(paper_id):
    summary = await getPaperSummary(paper_id)  
    if summary:
        return jsonify({'summary': summary})      
    else:
        return jsonify({'error': 'Paper not found'}), 404



# Replace 'YOUR_API_KEY' with your actual OpenAI API key
api_key = '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'
client = OpenAI(api_key=api_key)

csv_file = "data/publications.csv"

class PercentageAndPublication:
    def __init__(self, publication, percentage_of_similarity):
        self.publication = publication
        self.percentage_of_similarity = percentage_of_similarity

# Function to get paper summary
def getPaperSummary(paper_id):
    # Path to the CSV file
  
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

@app.route('/summarize/<paper_id>')
def summarize(paper_id):
    summary = getPaperSummary(paper_id)
    return jsonify({'summary': summary})

@app.route('/suggested', methods = ['POST'])
def getSuggested():
    '''
    url = f'https://api.semanticscholar.org/recommendations/v1/papers/forpaper/{publicationId}?fields=authors,title'

    response = requests.get(url)
    
    if response.status_code != 200:
        return jsonify({'error': f"Request failed with status code {response.status_code}: {response.text}"}), response.status_code
    '''

    fieldsOfStudy = request.json['fieldsOfStudy']
    current_publication_id = request.json['publication_id']
    csvPublications = getPublications()

    publications = [publication for publication in csvPublications if any(category in publication.category for category in fieldsOfStudy) and publication.semantic_paper_id != current_publication_id]
    
    publications = publications[:5]

    publicationId = current_publication_id
    url = f'https://api.semanticscholar.org/graph/v1/paper/{publicationId}?fields=abstract'
    current_abstract = requests.get(url).json()['abstract']
    
    listOfPercentagesAndPublications = []

    for publication in publications:
        publicationId = publication.semantic_paper_id
        url = f'https://api.semanticscholar.org/graph/v1/paper/{publicationId}?fields=abstract,title,openAccessPdf,authors,fieldsOfStudy,url'
        publicationObject = requests.get(url).json()
        abstract = requests.get(url).json()['abstract']
        prompt = f" TASK: Give me a percent of similarity of the following two texts. Focus on themes and fields of studies. Write a sentence: \"Percentage is {{number}}\" and add your estimated percetange of similarity. \n\n Text1:\n\n {abstract}\n\n Text2:\n\n {current_abstract}."
        payload = {
            "model": "mistralai/Mistral-7B-Instruct-v0.2",
            "prompt": prompt,
            "stop": "..",
            "max_tokens": 1500,
            "temperature": 0
        }       
        response = requests.post("https://late-wasps-joke.loca.lt/v1/completions", json = payload)   
        text = response.json()["choices"][0]["text"]
        match = re.findall(r'\d*%', str(text))
        match = [int(m.replace('%', '')) for m in match]
        if match.count!=0:
            percentage = match[0]
            if percentage >= 50:
                publicationObject = Publication(
                    publicationObject.get('paperId'),
                    publicationObject.get('url'),
                    publicationObject.get('title'),
                    publicationObject.get('openAccessPdf'),
                    publicationObject.get('authors'),
                    publicationObject.get('fieldsOfStudy'))

                listOfPercentagesAndPublications.append(PercentageAndPublication(publicationObject,percentage))
        
        if response.status_code !=200:
            return(f"Error: {response.status_code}, {response.text}")

        sorted_publications = sorted(listOfPercentagesAndPublications, key=lambda x: x.percentage_of_similarity, reverse=True)

    return jsonify([item.percentage_of_similarity for item in sorted_publications[:3]])




if __name__ == '__main__':
    app.run(debug=True, port=3600)
