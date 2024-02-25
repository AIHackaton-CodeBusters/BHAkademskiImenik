import requests
import fitz  # PyMuPDF
from openai import OpenAI

# Replace 'YOUR_API_KEY' with your actual OpenAI API key
api_key = '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'
client = OpenAI(api_key=api_key)

# URL of the PDF file
pdf_url = "https://arxiv.org/pdf/2303.16125.pdf"

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

# Close the PDF document
pdf_document.close()

# Using OpenAI to simplify a technical document
completion = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": "You are requested to simplify a technical document about multi-core quantum computing architectures."},
        {"role": "user", "content": "Simplify the document and include headings to make it understandable for people with limited knowledge on the subject."},
        {"role": "user", "content": "The document should be no longer than 2 pages."},
        {"role": "user", "content": "Here is the text: " + pdf_text}  # Providing the extracted text from the PDF
    ]
)

# Accessing the first message in the completion
response_message = completion.choices[0].message

# Printing the content of the response message
print(response_message.content)
