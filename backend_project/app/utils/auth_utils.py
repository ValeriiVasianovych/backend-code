from flask import request
import jwt
from app.config import Config
from app.extensions import mongo
from bson import ObjectId
from functools import wraps
from flask import jsonify
from .error_handlers import ServiceError

def get_current_user():
    token = None
    if 'Authorization' in request.headers:
        auth_header = request.headers['Authorization']
        try:
            token = auth_header.split(" ")[1]
            data = jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=['HS256'])
            user_id = ObjectId(data['user_id'])
            current_user = mongo.db.users.find_one({'_id': user_id})
            if not current_user:
                raise ServiceError('User not found', 401)
            return current_user
        except jwt.ExpiredSignatureError:
            raise ServiceError('Token has expired', 401)
        except jwt.InvalidTokenError:
            raise ServiceError('Invalid token', 401)
        except Exception as e:
            raise ServiceError('Authentication failed', 401)
    return None

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        current_user = get_current_user()
        if not current_user:
            raise ServiceError('Authentication required', 401)
        return f(current_user, *args, **kwargs)
    return decorated

def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            current_user = get_current_user()
            if not current_user:
                raise ServiceError('Authentication required', 401)
            if current_user.get('role') != role:
                raise ServiceError('Permission denied', 403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator 