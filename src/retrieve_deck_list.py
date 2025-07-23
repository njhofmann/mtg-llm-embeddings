import requests

response = requests.put('https://api.moxfield.com/v2/decks/all/_H-0ckJbgUeHxIF7cIqZJQ')
response.raise_for_status()
print(response.content)