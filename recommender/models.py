from django.db import models

class Genre(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

class Keyword(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

class Movie(models.Model):
    tmdb_id = models.IntegerField(unique=True)
    title = models.CharField(max_length=200)
    overview = models.TextField()
    release_date = models.DateField(null=True, blank=True)
    
    # ✅ Fixed poster field (Renamed to `poster_path`)
    poster_path = models.URLField(max_length=500, null=True, blank=True)  # Stores full poster URL

    vote_average = models.FloatField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    rating = models.FloatField(null=True, blank=True)

    genres = models.JSONField(default=list)  # Store genres as a list
    keywords = models.JSONField(default=list)  # Store keywords as a list
    cast = models.JSONField(default=list)  # Store top 5 cast members as a list
    crew = models.JSONField(default=dict)  # Store crew (Director, Writer) as a dictionary
    
    similarity = models.JSONField(default=dict)  # Store similarity scores as a dictionary

    category = models.CharField(
        max_length=20,
        choices=[("popular", "Popular"), 
                 ("top_rated", "Top Rated"), 
                 ("upcoming", "Upcoming"), 
                 ("now_playing", "Now Playing")], 
        default="popular"  # Temporary default
    )

    def __str__(self):
        return self.title

class Cast(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name="movie_cast")
    name = models.CharField(max_length=255)
    character = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.name} as {self.character}"

class Crew(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name="movie_crew")
    name = models.CharField(max_length=255)
    job = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.name} ({self.job})"
