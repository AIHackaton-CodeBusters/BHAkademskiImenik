import csv
import json

class Publication:
    def __init__(self, semantic_paper_id, url, title, open_access_pdf, authors, category):
        self.semantic_paper_id = semantic_paper_id
        self.url = url
        self.title = title
        self.open_access_pdf = open_access_pdf
        self.authors = authors
        self.category = category
    def to_dict(self):
        return {
            'semantic_paper_id': self.semantic_paper_id,
            'url': self.url,
            'title': self.title,
            'open_access_pdf': self.open_access_pdf,
            'authors': self.authors,
            'category': self.category
        }
    

def getPublications():
    publications = []
    
    with open('data/publications.csv', newline='', encoding='utf-8') as csvfile:
        csvreader = csv.DictReader(csvfile)
        for row in csvreader:
            authors = parse_category(row['authors']) 
            category = parse_category(row['category'])
            publication = Publication(
                row['SemanticPaperId'],
                row['url'],
                row['title'],
                row['openAccessPdf'],
                authors,
                category
            )
            publications.append(publication)

    return publications

def parse_category(category_str):
    try:
        if category_str != 'null':
            return json.loads(category_str)
        else:
            return []
    except json.JSONDecodeError:
        # Handle invalid JSON data here
        print(f"Invalid JSON data: {category_str}")
        return []

