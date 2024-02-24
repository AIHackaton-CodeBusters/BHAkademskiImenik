import csv
import json

def read_pdf_links_from_csv(csv_file):
    pdf_links = []
    with open(csv_file, 'r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            semantic_paper_id = row.get('SemanticPaperId')
            pdf_info = row.get('openAccessPdf')
            if pdf_info:
                try:
                    pdf_info_dict = json.loads(pdf_info)
                    pdf_url = pdf_info_dict.get('url')
                    if pdf_url:
                        pdf_links.append({'SemanticPaperId': semantic_paper_id, 'url': pdf_url})
                except json.JSONDecodeError:
                    print(f"Error decoding JSON: {pdf_info}")
    return pdf_links

# Path to the CSV file
csv_file = "data/publications.csv"

# Read PDF links from the CSV file
pdf_links = read_pdf_links_from_csv(csv_file)

# Print the PDF links
for pdf_link in pdf_links:
    print(pdf_link)
