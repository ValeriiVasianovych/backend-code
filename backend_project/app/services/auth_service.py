from flask import jsonify, session, url_for
import datetime
import secrets
import logging
from flask import jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import mongo
from datetime import datetime
import jwt
from app.config import Config
from bson.objectid import ObjectId

class AuthService:
    def create_user(self, email, password):
        if self.get_user_by_email(email):
            raise ValueError("User with this email already exists")
            
        hashed_password = generate_password_hash(password)
        user = {
            'email': email,
            'password': hashed_password,
            'created_at': datetime.utcnow(),
            'is_active': True
        }
        
        result = mongo.db.users.insert_one(user)
        user['_id'] = str(result.inserted_id)
        return user

    def verify_password(self, password, hashed_password):
        return check_password_hash(hashed_password, password)
        
    def get_user_by_email(self, email):
        return mongo.db.users.find_one({'email': email})
        
    def generate_tokens(self, user_id):
        access_token = self._generate_token(
            user_id,
            Config.JWT_ACCESS_TOKEN_EXPIRES
        )
        refresh_token = self._generate_token(
            user_id,
            Config.JWT_REFRESH_TOKEN_EXPIRES
        )
        return {
            'access_token': access_token,
            'refresh_token': refresh_token
        }
        
    def _generate_token(self, user_id, expires_delta):
        payload = {
            'user_id': str(user_id),
            'exp': datetime.utcnow() + expires_delta,
            'iat': datetime.utcnow()
        }
        return jwt.encode(payload, Config.JWT_SECRET_KEY, algorithm='HS256')

    def change_password(self, user_id, current_password, new_password):
        try:
            user = mongo.db.users.find_one({'_id': ObjectId(user_id)})
            if not user:
                raise ValueError('User not found')
            
            if not self.verify_password(current_password, user['password']):
                raise ValueError('Current password is incorrect')
            
            if not validate_password(new_password):
                raise ValueError('New password does not meet security requirements')
            
            hashed_password = self.hash_password(new_password)
            mongo.db.users.update_one(
                {'_id': ObjectId(user_id)},
                {'$set': {'password': hashed_password}}
            )
            
            return True
        except Exception as e:
            logger.error(f"Change password error: {str(e)}")
            raise