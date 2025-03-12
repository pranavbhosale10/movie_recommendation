import requests
from django.conf import settings
from django.db import transaction
from concurrent.futures import ThreadPoolExecutor
from recommender.models import Movie

# TMDB API Key
TMDB_API_KEY = settings.TMDB_API_KEY
TMDB_BASE_URL = "https://api.themoviedb.org/3"
CATEGORIES = ["popular", "top_rated", "upcoming", "now_playing"]

def fetch_movies_from_category(category):
    """Fetches movies for a given category from TMDB."""
    url = f"{TMDB_BASE_URL}/movie/{category}"
    params = {"api_key": TMDB_API_KEY, "language": "en-US", "page": 1}

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return {movie["id"]: category for movie in response.json().get("results", [])}
    except requests.RequestException as e:
        print(f"⚠ API error for category {category}: {e}")
        return {}

def get_movie_category_mapping():
    """Fetches movie categories in parallel for faster execution."""
    category_mapping = {}

    # Use threading to fetch data faster
    with ThreadPoolExecutor(max_workers=4) as executor:
        results = executor.map(fetch_movies_from_category, CATEGORIES)

    # Combine all category mappings
    for result in results:
        category_mapping.update(result)

    return category_mapping

def update_movie_categories():
    """Updates the category field for existing movies in the database using batch updates."""
    category_mapping = get_movie_category_mapping()
    
    movies_to_update = []
    
    for movie in Movie.objects.all():
        new_category = category_mapping.get(movie.tmdb_id, "popular")
        
        if movie.category != new_category:
            movie.category = new_category
            movies_to_update.append(movie)

    # Bulk update for faster execution
    if movies_to_update:
        with transaction.atomic():
            Movie.objects.bulk_update(movies_to_update, ["category"])
        print(f"✅ Updated {len(movies_to_update)} movies' categories.")

    print("🎉 Update complete!")

# Run the update function
if __name__ == "__main__":
    update_movie_categories()
