import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'diabeticare-secret-key-change-in-production'

    # Use /tmp on Vercel (serverless — ephemeral filesystem)
    if os.environ.get('VERCEL'):
        SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/diabeticare.db'
    else:
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
