import os
import secrets
import datetime
from dotenv import load_dotenv
from app.jwt_config import JWT_SECRET_KEY
from datetime import timedelta

load_dotenv()

class Config:
    # Базовые настройки
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key')
    
    # JWT настройки
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'your-jwt-secret-key')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
    # MongoDB настройки
    MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/your_database')
    
    # Дополнительные настройки безопасности
    JWT_TOKEN_LOCATION = ['headers']
    JWT_HEADER_NAME = 'Authorization'
    JWT_HEADER_TYPE = 'Bearer'
    
    # GitHub OAuth settings
    GITHUB_CLIENT_ID = os.getenv('GITHUB_CLIENT_ID')
    GITHUB_CLIENT_SECRET = os.getenv('GITHUB_CLIENT_SECRET')
    GITHUB_REDIRECT_URI = os.getenv('GITHUB_REDIRECT_URI', 'http://127.0.0.1:8080/github-callback')
    
    # Logging settings
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')