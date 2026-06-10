import os
from flask import Flask
from flask_login import LoginManager
from dotenv import load_dotenv
from models import db, User

load_dotenv()

app = Flask(__name__)

# Config
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'quizmaster-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///quizmaster.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please login to access this page.'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Register blueprints
from auth import auth
from quiz import quiz

app.register_blueprint(auth)
app.register_blueprint(quiz)

# Create tables
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)