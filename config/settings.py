# config/settings.py

import os

# Example: read from env variables or define defaults
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "event_dashboard")

# Possibly other settings, like secret keys, etc.
SECRET_KEY = os.getenv("SECRET_KEY", "mysecret123")
