from __future__ import absolute_import, unicode_literals
import os
import logging
from celery import Celery

# Set the default Django settings module for the 'celery' program
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

# Initialize Celery application
app = Celery('backend')

# Load Celery configuration from Django settings
app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

# Configure logging for Celery
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

try:
    # Auto-discover tasks from installed Django apps
    app.autodiscover_tasks()
    logger.info("Celery tasks discovered successfully.")
except Exception as e:
    logger.error(f"Error discovering Celery tasks: {e}")

@app.task(bind=True)
def debug_task(self):
    """ A simple debug task for Celery. """
    try:
        logger.info(f'Debug Task Executed: {self.request!r}')
        print(f'Request: {self.request!r}')
    except Exception as e:
        logger.error(f"Error executing debug task: {e}")
