# config/settings.py

import os

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "event_dashboard")

SECRET_KEY = os.getenv("SECRET_KEY", "mysecret123")
