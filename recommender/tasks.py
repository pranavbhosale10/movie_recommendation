from celery import shared_task
import logging
from .utils.fetch_movies import fetch_and_store_movies

# Set up logging
logger = logging.getLogger(__name__)

@shared_task
def fetch_movies_task():
    """Task to fetch and store movies periodically."""
    try:
        logger.info("Starting movie fetching task...")
        fetch_and_store_movies(pages=10)  # Adjust pages as needed
        logger.info("Movie fetching task completed successfully.")
        return "Movie fetching completed!"
    except Exception as e:
        logger.error(f"Error in fetch_movies_task: {e}")
        return f"Error: {e}"

from celery import shared_task


@shared_task
def add(x, y):
    return x + y

