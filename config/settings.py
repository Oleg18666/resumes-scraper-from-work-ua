"""Configuration settings for Work.ua scraper pipeline."""
import os
from typing import Dict, Any

# Base URL and endpoints
BASE_URL = "https://www.work.ua"
SEARCH_URL_TEMPLATE = f"{BASE_URL}/resumes-{{city}}-{{category}}/"
RESUME_URL_TEMPLATE = f"{BASE_URL}/resumes/{{resume_id}}/"

# HTTP Client settings
REQUEST_TIMEOUT = 30  # seconds
MAX_RETRIES = 3
RETRY_BACKOFF_FACTOR = 2  # exponential backoff: 2, 4, 8 seconds
REQUEST_DELAY = 1.0  # delay between requests to avoid rate limiting

# User-Agent rotation (to avoid detection)
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
]

# Database settings (PostgreSQL)
DB_CONFIG: Dict[str, Any] = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", 5432)),
    "database": os.getenv("DB_NAME", "workua_resumes"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", ""),
}

# Queue settings (RabbitMQ / Redis / Postgres LISTEN/NOTIFY)
QUEUE_TYPE = os.getenv("QUEUE_TYPE", "rabbitmq")  # "rabbitmq", "redis", "postgres"

# RabbitMQ settings
RABBITMQ_CONFIG = {
    "host": os.getenv("RABBITMQ_HOST", "localhost"),
    "port": int(os.getenv("RABBITMQ_PORT", 5672)),
    "username": os.getenv("RABBITMQ_USER", "guest"),
    "password": os.getenv("RABBITMQ_PASSWORD", "guest"),
    "queue_search": "workua_search_pages",
    "queue_resume": "workua_resume_pages",
}

# Redis settings
REDIS_CONFIG = {
    "host": os.getenv("REDIS_HOST", "localhost"),
    "port": int(os.getenv("REDIS_PORT", 6379)),
    "db": int(os.getenv("REDIS_DB", 0)),
    "password": os.getenv("REDIS_PASSWORD", None),
    "stream_search": "workua:search_pages",
    "stream_resume": "workua:resume_pages",
}

# Scraping settings
CATEGORIES = {
    "it": 1,
    "sales": 2,
    "management": 3,
    # Add more categories as needed
}

CITIES = {
    "kyiv": 39,
    "kharkiv": 26,
    "odesa": 51,
    "dnipro": 11,
    "lviv": 40,
    # Add more cities as needed
}

# Pagination settings
MAX_PAGES_PER_SEARCH = 100  # maximum pages to scrape per search query
RESUMES_PER_PAGE = 14  # approximate number of resumes per page

# Days filter for fresh resumes
DEFAULT_DAYS_FILTER = 30  # scrape resumes from last N days

# Logging settings
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_FILE = os.getenv("LOG_FILE", "logs/workua_scraper.log")

# Worker settings
WORKER_CONCURRENCY = int(os.getenv("WORKER_CONCURRENCY", 4))  # number of parallel workers
WORKER_PREFETCH_COUNT = 1  # number of tasks to prefetch per worker

# Photo download settings
DOWNLOAD_PHOTOS = True
MAX_PHOTO_SIZE_MB = 5
PHOTO_QUALITY = 85  # JPEG quality for compression
