import os
from dotenv import load_dotenv
from pathlib import Path

# Determine the base directory (adjust if needed)
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from the .env file
load_dotenv(BASE_DIR / '.env')


#Mongo database settings
MONGO_HOST     = os.getenv("MONGO_HOST", "mongodb")
MONGO_PORT     = os.getenv("MONGO_PORT", "27017")
MONGO_DB       = os.getenv("MONGO_DB", "event_dashboard")
MONGO_USER     = os.getenv("MONGO_USER", "")
MONGO_PASS     = os.getenv("MONGO_PASS", "")
MONGO_AUTHSRC  = os.getenv("MONGO_AUTHSRC", MONGO_DB)

# if MONGO_USER and MONGO_PASS:
#     MONGO_URI = (f"mongodb://{MONGO_USER}:{MONGO_PASS}"
#                  f"@{MONGO_HOST}:{MONGO_PORT}/{MONGO_DB}"
#                  f"?authSource={MONGO_AUTHSRC}")
# else:
#     MONGO_URI = f"mongodb://{MONGO_HOST}:{MONGO_PORT}/{MONGO_DB}"

MONGO_URI = "mongodb://localhost:27017"

# Load the GitHub token from the environment
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
GITHUB_SIGNATURE_KEY = os.getenv("GITHUB_SIGNATURE_KEY", "")


# Load the TAIGA token from the environment
TAIGA_TOKEN = os.getenv("TAIGA_TOKEN", "")
TAIGA_SIGNATURE_KEY = os.getenv("TAIGA_SIGNATURE_KEY", "")
TAIGA_USERNAME = os.getenv("TAIGA_USERNAME", "")
TAIGA_PASSWORD= os.getenv("TAIGA_PASSWORD", "")


# Load the webhook URLs from the environment to enable the deletion of webhooks
WEBHOOK_URL_GITHUB = os.getenv("WEBHOOK_URL_GITHUB", "")
WEBHOOK_URL_TAIGA = os.getenv("WEBHOOK_URL_TAIGA", "")