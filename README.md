# DiabetiCare

DiabetiCare is a comprehensive, centralized web application designed to empower individuals managing diabetes. It provides robust tools for tracking health metrics, managing medications, understanding nutrition, and participating in a supportive community.

## Features

* **Health Tracking Analytics:** Log, track, and visualize blood glucose levels, physical activities, and meal macros.
* **AI-Powered Diet Insights:** Utilizes Google Generative AI to analyze meal compositions and offer dietary insights.
* **Medication & Appointment Management:** Keep a rigorous log of medication adherence and never miss clinical checkups with an integrated appointments tracker.
* **Education Curriculum:** Access structured educational modules testing knowledge with adaptive quizzes covering diabetes basics, diet, exercise, foot care, and complications.
* **Gamification:** Earn badges and accomplish goals by maintaining healthy streaks and target health metrics.
* **Supportive Community:** Participate in forums, post questions, share tips, and send secure messages to peers or healthcare providers.
* **Accessibility Focused:** Built-in settings for high-contrast viewing, customizable font sizes, and multiple language support.

## Tech Stack

* **Backend:** Python, Flask, SQLAlchemy 
* **Database:** SQLite (Development) / PostgreSQL (Production)
* **Authentication:** Flask-Login, Flask-Bcrypt, Magic Link login via Flask-Mail
* **Frontend:** Jinja2 templates, Custom CSS/JS (Mobile-Responsive)
* **Integrations:** Google Generative AI (Gemini), ReportLab, APScheduler

## Prerequisites

Before you begin, ensure you have met the following requirements:
* Python 3.9+ installed
* PostgreSQL (Optional, if moving to production)
* A valid Google Gemini API Key

## Installation & Local Setup

1. **Clone the repository and enter the directory:**
    ```bash
    git clone https://github.com/mcgini100/diabeticare.git
    cd diabeticare
    ```

2. **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    
    # On Windows:
    .\venv\Scripts\activate
    # On macOS/Linux:
    source venv/bin/activate
    ```

3. **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4. **Set up environment variables:**
    Create a `.env` file in the root directory based on `.env.production` concepts. You will need at least:
    ```env
    SECRET_KEY=your_super_secret_key
    FLASK_APP=main.py
    FLASK_DEBUG=1
    DATABASE_URL=sqlite:///diabeticare.db
    MAIL_SERVER=smtp.yourmail.com
    MAIL_PORT=587
    MAIL_USE_TLS=True
    MAIL_USERNAME=your_email@domain.com
    MAIL_PASSWORD=your_email_password
    GEMINI_API_KEY=your_google_gemini_api_key
    ```

5. **Initialize the Database:**
    The application will automatically create the database and seed initial education modules upon first run.
    ```bash
    flask run
    ```

6. **Open the Application:**
    Navigate to `http://127.0.0.1:5000` in your web browser.

## Project Structure

```text
DiabetiCare/
├── api/                  # API endpoints and logic
├── images/               # Media and graphical assets
├── static/               # CSS, JS, and Service Workers (PWA)
├── templates/            # Jinja2 HTML templates
├── views/                # Flask Blueprints (Controllers)
├── main.py               # Application factory and entry point
├── models.py             # SQLAlchemy Database Models
├── forms.py              # WTForms classes
├── extensions.py         # Flask Extensions initialization
├── config.py             # Application configuration class
├── ai_service.py         # Google Generative AI integration logic
├── requirements.txt      # Python dependencies
└── vercel.json           # Vercel deployment configuration
```

## 🚀 Deployment

DiabetiCare is configured to easily deploy to Vercel or any standard WSGI/ASGI server. 
When deploying, make sure to set the underlying environment variables in your hosting provider's dashboard and use PostgreSQL instead of SQLite (update `DATABASE_URL`).
