import requests
import fitz  

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

# Close the PDF document
pdf_document.close()

# Print or use the extracted text
print(page)
