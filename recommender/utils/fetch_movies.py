import time
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from django.conf import settings
from django.db import transaction
from django.db.utils import IntegrityError
from django.core.exceptions import ValidationError
from ..models import Movie

# TMDB API Key
TMDB_API_KEY = settings.TMDB_API_KEY

# TMDB API URLs
TMDB_BASE_URL = "https://api.themoviedb.org/3"
POSTER_BASE_URL = "https://image.tmdb.org/t/p/w500"

# Categories to fetch movies from
CATEGORIES = ["popular", "top_rated", "upcoming", "now_playing"]

def fetch_movie_details(movie_id):
    """Fetches genres, keywords, cast, and crew for a given movie."""
    endpoints = {
        "details": f"{TMDB_BASE_URL}/movie/{movie_id}",
        "keywords": f"{TMDB_BASE_URL}/movie/{movie_id}/keywords",
        "credits": f"{TMDB_BASE_URL}/movie/{movie_id}/credits"
    }

    results = {}
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = {key: executor.submit(requests.get, url, {"api_key": TMDB_API_KEY}) for key, url in endpoints.items()}
        
        for key, future in futures.items():
            try:
                response = future.result()
                if response.status_code == 200:
                    results[key] = response.json()
                else:
                    print(f"⚠ API Error: {key} for movie {movie_id} - Status Code {response.status_code}")
                    results[key] = {}
            except requests.RequestException as e:
                print(f"⚠ Network Error: {key} for movie {movie_id} - {e}")
                results[key] = {}

    # Extract necessary details safely
    details = results.get("details", {})
    credits = results.get("credits", {})

    return {
        "genres": [genre["name"] for genre in details.get("genres", [])],
        "keywords": [keyword["name"] for keyword in results.get("keywords", {}).get("keywords", [])],
        "cast": [actor["name"] for actor in credits.get("cast", [])[:5]],  # Top 5 actors
        "crew": [
            crew_member["name"]
            for crew_member in credits.get("crew", [])
            if crew_member["job"] in ["Director", "Writer"]
        ],
    }

def fetch_and_store_movies(pages=150):
    """Fetches movies from TMDB API and stores them in the database efficiently."""

    # ❌ Delete old movies that have no poster
    print("🗑️ Removing movies without a valid poster...")
    Movie.objects.filter(poster_path="").delete()

    all_movie_objects = []  # List for bulk insertion

    for category in CATEGORIES:
        print(f"\n🔄 Fetching movies from category: {category}...\n")

        for page in range(1, pages + 1):
            url = f"{TMDB_BASE_URL}/movie/{category}"
            params = {"api_key": TMDB_API_KEY, "language": "en-US", "page": page}

            try:
                response = requests.get(url, params=params)
                response.raise_for_status()
                data = response.json()
            except requests.RequestException as e:
                print(f"⚠ Failed to fetch page {page} from {category}: {e}")
                continue

            movies_fetched = 0

            # Fetch additional details in parallel
            with ThreadPoolExecutor(max_workers=5) as executor:
                future_details = {movie["id"]: executor.submit(fetch_movie_details, movie["id"]) for movie in data.get("results", [])}

                for movie_data in data.get("results", []):
                    movie_id = movie_data["id"]
                    poster_path = movie_data.get("poster_path")

                    # ✅ Ensure full poster URL is stored
                    full_poster_url = f"{POSTER_BASE_URL}{poster_path}" if poster_path else ""

                    # Ensure release_date is valid
                    release_date = movie_data.get("release_date")
                    if release_date and len(release_date.split("-")) != 3:
                        print(f"⚠ Skipping movie {movie_id} due to invalid release date: {release_date}")
                        continue

                    # Skip movies with no poster
                    if not full_poster_url:
                        print(f"⚠ Skipping movie {movie_id} because it has no poster.")
                        continue

                    # Get fetched details
                    details = future_details[movie_id].result()

                    # Skip duplicate movies
                    if Movie.objects.filter(tmdb_id=movie_id).exists():
                        print(f"🔁 Movie {movie_id} already exists, skipping...")
                        continue

                    # ✅ Store movie data for bulk insertion
                    all_movie_objects.append(
                        Movie(
                            tmdb_id=movie_id,
                            title=movie_data["title"],
                            description=movie_data["overview"],
                            release_date=release_date or None,
                            rating=movie_data.get("vote_average"),
                            poster_path=full_poster_url,  # ✅ Store full URL as `poster_path`
                            category=category,  # Categorize movies
                            genres=details["genres"],  
                            keywords=details["keywords"],  
                            cast=details["cast"],  
                            crew=details["crew"],  
                        )
                    )

                    movies_fetched += 1

            print(f"✅ Page {page}: Added {movies_fetched} new movies.")

    # ✅ Bulk insert all movies at once (MUCH FASTER)
    if all_movie_objects:
        try:
            with transaction.atomic():
                Movie.objects.bulk_create(all_movie_objects, ignore_conflicts=True)
            print(f"\n🎉 Successfully added {len(all_movie_objects)} new movies.")
        except (ValidationError, IntegrityError) as e:
            print(f"⚠ Database error during bulk insertion: {e}")

    print("\n🎉 Movie fetching complete!")
