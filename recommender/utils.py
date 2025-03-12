import requests
from django.conf import settings

def test_tmdb_api():
    url = f"https://api.themoviedb.org/3/movie/popular?api_key={settings.TMDB_API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": "API Key is invalid or there's an issue with the API."}
