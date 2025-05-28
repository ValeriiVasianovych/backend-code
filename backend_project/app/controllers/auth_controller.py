from flask import request, redirect, url_for
from app.controllers.base_controller import BaseController
from app.models.user import User
from app.services.auth_service import AuthService
from app.utils.validators import validate_email, validate_password
from app.utils.error_handlers import ServiceError
import logging

logger = logging.getLogger(__name__)

class AuthController(BaseController):
    def __init__(self):
        self.auth_service = AuthService()

    def register(self):
        try:
            data = request.get_json()
            if not data:
                return self.error_response("No data provided", 400)

            email = data.get('email')
            password = data.get('password')
            
            if not all([email, password]):
                return self.error_response("Required fields are missing", 400)
                
            if not validate_email(email):
                return self.error_response("Invalid email format", 400)
                
            if not validate_password(password):
                return self.error_response("Password does not meet security requirements", 400)
            
            # Проверяем, существует ли пользователь с таким email
            existing_user = User.find_by_email(email)
            if existing_user:
                return self.error_response("User with this email already exists", 409)
                
            user = User.create({
                'email': email,
                'password': password,
                'is_active': True
            })
            
            tokens = self.auth_service.generate_tokens(user['_id'])
            
            return redirect(url_for('rentals.cars_page', 
                access_token=tokens['access_token'],
                refresh_token=tokens['refresh_token']))
            
        except ValueError as e:
            return self.error_response(str(e), 400)
        except Exception as e:
            logger.error(f"Registration error: {str(e)}")
            return self.error_response("Internal server error", 500)

    def login(self):
        try:
            data = request.get_json()
            if not data:
                return self.error_response("No data provided", 400)

            email = data.get('email')
            password = data.get('password')
            
            if not all([email, password]):
                return self.error_response("Required fields are missing", 400)
                
            user = User.find_by_email(email)
            if not user:
                return self.error_response("Invalid email or password", 401)
                
            if not User.verify_password(password, user['password']):
                return self.error_response("Invalid email or password", 401)
                
            tokens = self.auth_service.generate_tokens(user['_id'])
            
            return redirect(url_for('rentals.cars_page', 
                access_token=tokens['access_token'],
                refresh_token=tokens['refresh_token']))
            
        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            return self.error_response("Internal server error", 500)

    def refresh_token(self):
        try:
            data = request.get_json()
            if not data:
                return self.error_response("No data provided", 400)

            refresh_token = data.get('refresh_token')
            
            if not refresh_token:
                return self.error_response("Refresh token is missing", 400)
                
            try:
                payload = self.auth_service.verify_token(refresh_token)
                user_id = payload['user_id']
                
                user = User.find_by_id(user_id)
                if not user:
                    return self.error_response("User not found", 401)
                    
                tokens = self.auth_service.generate_tokens(user_id)
                return self.success_response(
                    data={'tokens': tokens},
                    message="Token refreshed successfully"
                )
                
            except Exception as e:
                return self.error_response(str(e), 401)
                
        except Exception as e:
            logger.error(f"Refresh token error: {str(e)}")
            return self.error_response("Internal server error", 500)

    def get_users(self, current_user):
        try:
            users = User.get_all_users()
            return self.success_response(data={'users': users})
        except Exception as e:
            logger.error(f"Get users error: {str(e)}")
            return self.error_response("Internal server error", 500) 