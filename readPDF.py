import requests
import PyPDF2
from io import BytesIO

def read_pdf_from_url(pdf_url):
    # Send a GET request to the URL to fetch the PDF content
    response = requests.get(pdf_url)
    
    # Check if the request was successful
    if response.status_code == 200:
        # Read the content of the PDF
        pdf_content = BytesIO(response.content)
        
        # Create a PDF file reader object
        pdf_reader = PyPDF2.PdfFileReader(pdf_content)
        
        # Read each page of the PDF
        for page_num in range(pdf_reader.numPages):
            page = pdf_reader.getPage(page_num)
            print(page.extractText())  # Extract text from the page

# Example usage
pdf_url = "https://www.aclweb.org/anthology/N18-3011.pdf"
read_pdf_from_url(pdf_url)
