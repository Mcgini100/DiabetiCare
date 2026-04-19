# DiabetiCare - Project Methodology

## 1. Project Overview
**DiabetiCare** is a comprehensive, centralized web application designed to empower individuals with diabetes to manage their condition effectively. The core philosophy of the project is to bridge the gap between medical advice and daily lifestyle management by providing tools for rigorous tracking, ongoing education, and community support in a single, accessible platform.

## 2. Research & Problem Identification
Living with diabetes requires constant vigilance regarding blood sugar levels, medication intake, diet, and physical activity. Traditional management often involves disjointed tools—paper logs for glucose, different apps for diet and exercise, and static pamphlets for education. 
DiabetiCare solves this by integrating:
- Data logging (glucose, meals, exercise)
- Medical adherence (medication and appointment reminders)
- Knowledge empowerment (educational modules and quizzes)
- Social support (forums and direct messaging)

## 3. System Architecture & Tech Stack
The application is built as a monolithic web service using a traditional client-server architecture.
- **Backend Framework:** Python with Flask, chosen for its lightweight nature, extensibility, and robust ecosystem for web applications.
- **Database:** Relational database managed through SQLAlchemy (SQLite for development/local setup and PostgreSQL for production).
- **Authentication:** Custom passwordless Magic Link authentication using Flask-Mail, enhanced with secure token generation (itsdangerous), alongside traditional auth mechanisms.
- **Frontend:** Jinja2 templating combined with custom responsive CSS/JS, ensuring high performance and SEO compatibility.
- **AI Integration:** Google Generative AI is utilized for intelligent dietary analysis of logged meals.

## 4. Core Modules & Implementation Strategy
1. **Health Tracking & Analytics:**
   - *Glucose:* Logs and categorizes glucose levels (from "critical low" to "critical high") and correlates them with meal contexts.
   - *Diet:* Users log meals and nutritional macros. An AI integration analyzes meal compositions.
   - *Exercise & Medication:* Comprehensive trackers with an event-logging system to maintain adherence histories.
2. **Education & Assessment:**
   - A structured curriculum (modules ranging from Basics to Foot Care) combined with an adaptive quiz system to test and reinforce user knowledge.
   - Self-assessment forms that calculate risk scores and provide immediate feedback.
3. **Gamification & Engagement:**
   - Integrates Goals and Badges. Users define targets (e.g., maintain a target glucose level) and are rewarded with badges, promoting continuous engagement.
4. **Community and Provider Communication:**
   - Secure forums for peer support.
   - A secure messaging module designed for direct communication or sharing logs (such as glucose or medication reports) with healthcare providers or peers.

## 5. Design Principles & UX
- **Accessibility First:** The schema includes preferences for font size, high-contrast modes, and language localization (via Flask-Babel), ensuring the app is usable by visually impaired or elderly users.
- **Mobile-Responsive:** The interface is built to function flawlessly across desktop and mobile devices, acknowledging that health tracking predominantly happens on the go.
- **Privacy & Security:** Sensitive medical data is tied strictly to user IDs with CSRF protection enforced across all forms.

## 6. Deployment Methodology
The application is structured for easy deployment to cloud platforms like Vercel (evidenced by `vercel.json`), utilizing a standard WSGI/ASGI entry point (`main.py` -> `app`). Configuration is strictly environment-based (`.env` and `.env.production`), ensuring secure handling of database URLs, email credentials, and AI API keys.
