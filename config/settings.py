# config/settings.py

import os
from dotenv import load_dotenv
from pathlib import Path

# Determine the base directory (adjust if needed)
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from the .env file
load_dotenv(BASE_DIR / '.env')


#Mongo database settings
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "event_dashboard")

# Load the GitHub token from the environment
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "fallback_github_token")
GITHUB_SIGNATURE_KEY = os.getenv("GITHUB_SIGNATURE_KEY", "")


# Load the TAIGA token from the environment
TAIGA_TOKEN = os.getenv("TAIGA_TOKEN", "")
TAIGA_SIGNATURE_KEY = os.getenv("TAIGA_SIGNATURE_KEY", "")
TAIGA_USERNAME = os.getenv("TAIGA_USERNAME", "")
TAIGA_PASSWORD= os.getenv("TAIGA_PASSWORD", "")


WEBHOOK_URL_GITHUB = os.getenv("WEBHOOK_URL_GITHUB", "")
WEBHOOK_URL_TAIGA = os.getenv("WEBHOOK_URL_TAIGA", "")