import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from .models import Movie

def create_similarity_matrix():
    """
    Generate a similarity matrix based on genres, keywords, cast, and description.
    Store only the top 20 similar movies in the Movie model.
    """
    movies = list(Movie.objects.all())

    if not movies:
        print("No movies found in the database.")
        return

    # Create DataFrame from Movie objects
    data = {
        "id": [movie.tmdb_id for movie in movies],
        "title": [movie.title for movie in movies],
        "genres": [" ".join(movie.genres) if movie.genres else "" for movie in movies],
        "keywords": [" ".join(movie.keywords) if movie.keywords else "" for movie in movies],
        "cast": [" ".join(movie.cast[:3]) if movie.cast else "" for movie in movies],  # Top 3 actors
        "crew": [movie.crew[0] if movie.crew else "" for movie in movies],  # Only the director
        "description": [movie.description if movie.description else "" for movie in movies],
    }

    df = pd.DataFrame(data)

    # Assign weights to features (giving higher weight to important ones)
    df["combined_features"] = (
        df["genres"] * 3 + " " +  # Higher weight for genres
        df["keywords"] * 2 + " " +  # Higher weight for keywords
        df["cast"] + " " +  # Normal weight for cast (top 3 actors)
        df["crew"] + " " +  # Only director
        df["description"]  # Normal weight for description
    )

    # Vectorization using TF-IDF
    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf_matrix = vectorizer.fit_transform(df["combined_features"])

    # Compute cosine similarity
    cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)

    # Store only the top 20 similar movies
    for idx, movie in enumerate(movies):
        similarity_scores = {
            int(df["id"][i]): float(cosine_sim[idx][i])
            for i in np.argsort(cosine_sim[idx])[-21:-1]  # Top 20 (excluding itself)
        }
        movie.similarity = similarity_scores
        movie.save()

    print("✅ Improved similarity matrix created and stored successfully!")
