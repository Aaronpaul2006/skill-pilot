import os
from dotenv import load_dotenv
from datetime import timedelta

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'skillpilot_super_secret_2024'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///skillpilot.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = True
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')

    # Session security
    SESSION_COOKIE_SECURE = False      # True in production (HTTPS)
    SESSION_COOKIE_HTTPONLY = True     # Prevent JS access to cookies
    SESSION_COOKIE_SAMESITE = 'Lax'   # CSRF protection
    PERMANENT_SESSION_LIFETIME = timedelta(seconds=1800)  # 30 min session timeout

    # Security headers
    WTF_CSRF_ENABLED = False           # Manual CSRF via context processor

