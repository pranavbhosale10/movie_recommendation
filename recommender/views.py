from django.db.models import Q
from django.shortcuts import render, get_object_or_404
from .models import Movie
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Base URL for TMDB posters
BASE_POSTER_URL = "https://image.tmdb.org/t/p/w500"

def movie_list(request):
    """
    View to display a list of movies with search and sorting functionality.
    """
    query = request.GET.get('q', '')  # Fetch the search query
    sort = request.GET.get('sort', 'title')  # Default sorting by title

    # Filter movies based on the search query (title or overview)
    movies = Movie.objects.all()
    if query:
        movies = movies.filter(Q(title__icontains=query) | Q(description__icontains=query))

    # Apply sorting
    if sort:
        movies = movies.order_by(sort)

    # Ensure each movie has a full poster URL
    for movie in movies:
        if movie.poster_path:
            if not movie.poster_path.startswith("http"):
                movie.poster_path = BASE_POSTER_URL + movie.poster_path
        else:
            movie.poster_path = "/static/images/placeholder.png"  # Fallback image

    return render(request, 'recommender/movie_list.html', {
        'movies': movies,
        'query': query,
        'sort': sort,
    })

def movie_detail(request, id):
    """
    View to display detailed information about a specific movie and fetch similar movies.
    """
    movie = get_object_or_404(Movie, id=id)

    # Ensure full poster URL
    if movie.poster_path:
        if not movie.poster_path.startswith("http"):
            movie.poster_path = BASE_POSTER_URL + movie.poster_path
    else:
        movie.poster_path = "/static/images/placeholder.png"

    # Fetch similar movies
    similar_movies = get_similar_movies(movie)

    # Debugging poster paths
    print(f"Movie: {movie.title}, Poster: {movie.poster_path}")
    for rec in similar_movies:
        print(f"Similar Movie: {rec.title}, Poster: {rec.poster_path}")

    return render(request, 'recommender/movie_detail.html', {
        'movie': movie,
        'similar_movies': similar_movies,
    })

def get_similar_movies(movie):
    """
    Fetches similar movies using content-based filtering based on genres and descriptions.
    """
    try:
        # Get all movies from the database
        movies = list(Movie.objects.all().values("id", "title", "genres", "description", "poster_path"))

        # Convert to DataFrame
        df = pd.DataFrame(movies)

        if df.empty:
            return []

        # Fill missing values
        df.fillna("", inplace=True)

        # Combine genres and description to create a feature for similarity
        df["combined_features"] = df["genres"].astype(str) + " " + df["description"].astype(str)

        # Apply TF-IDF Vectorization
        vectorizer = TfidfVectorizer(stop_words="english")
        tfidf_matrix = vectorizer.fit_transform(df["combined_features"])

        # Compute cosine similarity
        similarity_matrix = cosine_similarity(tfidf_matrix, tfidf_matrix)

        # Find the index of the selected movie
        if movie.id not in df["id"].values:
            return []

        idx = df[df["id"] == movie.id].index[0]

        # Get similarity scores and sort them
        similar_scores = list(enumerate(similarity_matrix[idx]))
        similar_scores = sorted(similar_scores, key=lambda x: x[1], reverse=True)[1:7]  # Top 6 similar movies

        # Fetch similar movie IDs
        similar_movie_ids = [df.iloc[i[0]]["id"] for i in similar_scores]

        # Get movie objects for similar movies
        similar_movies = Movie.objects.filter(id__in=similar_movie_ids)

        # Ensure full poster URLs
        for movie in similar_movies:
            if movie.poster_path:
                if not movie.poster_path.startswith("http"):
                    movie.poster_path = BASE_POSTER_URL + movie.poster_path
            else:
                movie.poster_path = "/static/images/placeholder.png"

        return similar_movies

    except Exception as e:
        print(f"Error in fetching similar movies: {e}")
        return []
