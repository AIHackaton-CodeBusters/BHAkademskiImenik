import requests
import fitz  # PyMuPDF
from collections import Counter
import re
# URL of the PDF file
pdf_url = "https://aclanthology.org/N18-3011.pdf"
# Download the PDF content
response = requests.get(pdf_url)
pdf_bytes = response.content
# Open the PDF using PyMuPDF
pdf_document = fitz.open("pdf", pdf_bytes)
# Initialize an empty string to store the text content
pdf_text = ""
# Iterate through each page and extract text
for page_number in range(pdf_document.page_count):
    page = pdf_document[page_number]
    pdf_text += page.get_text()
# Search for the first appearance of the substring "References" from the end of the document
index_of_reference = pdf_text.rfind("References")
# Check if the substring is found
if index_of_reference != -1:
    # Truncate the text to keep only the content before the reference
    truncated_text = pdf_text[:index_of_reference]
    # Replace '-\n' with ''
    modified_text1 = truncated_text.replace('-\n', '')
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
    # Print or use the modified text
    print("Top 5 most used words:", top_5_words)
    print("\nFinal Output (one paragraph without newlines):")
    print(final_output)
else:
    print("Substring 'References' not found in the document.")
# Close the PDF document
pdf_document.close()
# Your final_output
final_output = ' '.join(sentences_with_top_words)
# API endpoint
api_endpoint = "https://late-wasps-joke.loca.lt/v1/completions"
# Payload for the API request
payload = {
    "model": "mistralai/Mistral-7B-Instruct-v0.2",
    "prompt": " TASK: Rewrite the following scientific text in one paragraph for a non-educated human.\n\n Text:\n\n {}".format(final_output),
    "stop": "..",
    "max_tokens": 1500,
    "temperature": 0
}
# Make the API request
response = requests.post(api_endpoint, json=payload)
# Check the response
if response.status_code == 200:
    # Extract and print the text after the colon in 'text' attribute
    api_response_text = response.json()['choices'][0]['text']
    extracted_text = api_response_text.split(':', 1)[-1].strip()
    print("Extracted Text:")
    print(extracted_text)
else:
    # Print an error message if the request was not successful
    print(f"Error: {response.status_code}, {response.text}")