# config.py
import os

# class Config:
#     SECRET_KEY = os.environ.get('SECRET_KEY') or 'a_secret_key'
#     SQLALCHEMY_DATABASE_URI = 'sqlite:///learning_league.db'
#     SQLALCHEMY_TRACK_MODIFICATIONS = False

import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'a_secret_key'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///learning_league.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(os.getcwd(), 'app/static/uploads')  # Set the folder for uploaded files
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}  # Set the allowed file extensions for uploaded files