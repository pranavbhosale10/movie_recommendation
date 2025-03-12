import requests
from decouple import config
from .models import Movie

# Get TMDB API key from environment variables
TMDB_API_KEY = config('TMDB_API_KEY')

# Base URL for TMDB API
BASE_URL = "https://api.themoviedb.org/3"

def fetch_popular_movies():
    """
    Fetch a list of popular movies from TMDB.
    """
    url = f"{BASE_URL}/movie/popular"
    params = {
        "api_key": TMDB_API_KEY,
        "language": "en-US",
        "page": 1
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json().get("results", [])
    else:
        print(f"Error fetching popular movies: {response.status_code}")
        return []

def fetch_movie_details(movie_id):
    """
    Fetch details of a specific movie using its TMDB ID.
    """
    url = f"{BASE_URL}/movie/{movie_id}"
    params = {
        "api_key": TMDB_API_KEY,
        "language": "en-US"
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching movie details: {response.status_code}")
        return None


def populate_movies():
    """
    Fetch popular movies from TMDB and save them to the database.
    """
    movies = fetch_popular_movies()
    for movie in movies:
        Movie.objects.update_or_create(
            tmdb_id=movie["id"],
            defaults={
                "title": movie["title"],
                "overview": movie["overview"],
                "release_date": movie["release_date"],
                "poster_path": f"https://image.tmdb.org/t/p/w500{movie['poster_path']}",
                "vote_average": movie["vote_average"],
            },
        )
    print("Database populated with popular movies!")