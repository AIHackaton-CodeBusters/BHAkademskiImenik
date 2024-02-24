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
for page_number in range(2):
    page = pdf_document[page_number]
    pdf_text += page.get_text()

# Close the PDF document
pdf_document.close()

# Check if the text contains 'Abstract' or 'Introduction'
abstract_index = pdf_text.find('Abstract')
introduction_index = pdf_text.find('Introduction')

# Determine where to start the text
start_index = min(filter(lambda x: x != -1, [abstract_index, introduction_index]))

# Cut the text from the starting index
cut_pdf_text = pdf_text[start_index:]

# Print or use the extracted text
print(cut_pdf_text)