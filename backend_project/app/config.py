import os
import secrets
import datetime
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Базовые настройки
    SECRET_KEY = os.environ.get('SECRET_KEY') or secrets.token_hex(32)
    
    # JWT настройки
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", secrets.token_hex(32))
    JWT_ACCESS_TOKEN_EXPIRES = datetime.timedelta(minutes=15)
    JWT_REFRESH_TOKEN_EXPIRES = datetime.timedelta(days=7)
    
    # MongoDB настройки
    MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/car_rental')
    
    # Дополнительные настройки безопасности
    JWT_TOKEN_LOCATION = ['headers']
    JWT_HEADER_NAME = 'Authorization'
    JWT_HEADER_TYPE = 'Bearer'