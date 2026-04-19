import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'diabeticare-secret-key-change-in-production'
    
    # Google OAuth
    GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
    GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')

    # Email Configuration
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'True').lower() in ['true', '1', 't']
    MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL', 'False').lower() in ['true', '1', 't']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', MAIL_USERNAME)

    # Database: Use DATABASE_URL env var for production (Neon PostgreSQL)
    # Falls back to SQLite for local development
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'diabeticare.db')

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Babel / i18n
    BABEL_DEFAULT_LOCALE = 'en'
    BABEL_DEFAULT_TIMEZONE = 'Africa/Harare'
    LANGUAGES = {
        'en': 'English',
        'sn': 'Shona',
        'nd': 'Ndebele'
    }

    # Upload settings
    if os.environ.get('VERCEL'):
        UPLOAD_FOLDER = '/tmp/uploads'
    else:
        UPLOAD_FOLDER = os.path.join(basedir, 'static', 'uploads')
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5 MB

    # Glucose thresholds (mmol/L)
    GLUCOSE_LOW = 4.0
    GLUCOSE_NORMAL_MIN = 4.0
    GLUCOSE_NORMAL_MAX = 7.0
    GLUCOSE_HIGH = 10.0
    GLUCOSE_CRITICAL_HIGH = 13.9
    GLUCOSE_CRITICAL_LOW = 3.0
