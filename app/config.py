import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-change-in-production")
    SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
    SUPABASE_ANON_KEY = os.environ.get("SUPABASE_ANON_KEY", "")
    APP_URL = os.environ.get(
        "APP_URL", os.environ.get("FLASK_APP_URL", "http://127.0.0.1:5000")
    )
