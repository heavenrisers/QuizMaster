# 🧠 QuizMaster – Quiz Platform

A full-stack quiz web application where users can create quizzes, attempt them with a countdown timer, and track their performance through analytics.

## Features
- 🔐 User Authentication (Signup, Login, Logout)
- 📝 Create quizzes with multiple choice questions
- ⏱️ Attempt quizzes with real-time countdown timer
- 📋 Quiz history with scores and dates
- 📊 Analytics dashboard with topic-wise performance chart
- ⚠️ Automatic weak topic detection (below 50%)

## Tech Stack
- **Backend:** Python, Flask, Flask-SQLAlchemy, Flask-Login
- **Database:** SQLite
- **Frontend:** HTML, CSS, JavaScript, Chart.js
- **Security:** Werkzeug password hashing

## Setup & Run

1. Clone the repository
git clone https://github.com/heavenrisers/QuizMaster.git
cd QuizMaster

2. Create virtual environment

3. Install dependencies
pip install flask flask-sqlalchemy flask-login werkzeug python-dotenv

4. Run the app