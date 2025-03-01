import requests

API_KEY = 'apikey'  #api test

url = 'https://ws.audioscrobbler.com/2.0/'
params = {
    'method': 'chart.gettopartists',
    'api_key': API_KEY,
    'format': 'json'
}

response = requests.get(url, params=params)

if response.status_code == 200:
    print(response.json())
else:
    print(f"Hata: {response.status_code}, Mesaj: {response.text}")
