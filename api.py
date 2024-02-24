import requests

# Define the API endpoint URL
url = 'https://api.semanticscholar.org/graph/v1/paper/search'

# More specific query parameter
query_params = {'query': 'quantum computing'}

# Directly define the API key (Reminder: Securely handle API keys in production environments)
api_key = 'NmKaEcYLf3N5DojI0Ajv26dc804QvjV4BwtLdFv1'  # Replace with the actual API key

# Define headers with API key
headers = {'x-api-key': api_key}

# Send the API request
response = requests.get(url, params=query_params, headers=headers)

# Check response status
if response.status_code == 200:
   response_data = response.json()
   # Process and print the response data as needed
   print(response_data)
else:
   print(f"Request failed with status code {response.status_code}: {response.text}")