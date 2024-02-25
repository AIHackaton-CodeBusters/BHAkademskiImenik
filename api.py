import csv
import requests
import fitz  
import json
import requests
import re
from readPublicationsCvs import getPublications, Publication
from openai import OpenAI
from flask import Flask, jsonify,request

app = Flask(__name__)

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
            percentage = match
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

    return jsonify([item.publication.to_dict() for item in sorted_publications[:3]])

if __name__ == '__main__':
    app.run(debug=True, port=3000)