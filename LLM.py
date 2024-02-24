import requests

# Server URL, change server_url string with one provided
# Access this link at the beginning with the password provided through any browser
server_url = "https://eighty-shrimps-raise.loca.lt"
completions_endpoint = server_url + "/v1/completions"
chat_completions_endpoint = server_url + "/v1/chat/completions"

# Create payload for text generation
text_generation_payload = {
    "model": "mistralai/Mistral-7B-Instruct-v0.2",
    "prompt": "Who am I?",
    "temperature": 0,
    "stop": ".",
    "max_tokens": 50
}

# Send text generation request
response = requests.post(completions_endpoint, json=text_generation_payload)

# Check response status
if response.status_code == 200:
    # Extract generated text
    generated_text = response.json()['choices'][0]['text']
    print("Generated text:", generated_text)
else:
    print("Failed to get a response from the server")
    print("Status code:", response.status_code)
    print("Response content:", response.text)


