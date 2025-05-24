from functools import wraps
from flask import request, jsonify
import jwt
from app.config import Config
from app.extensions import mongo
from bson import ObjectId

def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization')

        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]

        if not token:
            return jsonify({'error': 'Authorization token is missing'}), 401

        try:
            payload = jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=['HS256'])
            current_user = mongo.db.users.find_one({'_id': ObjectId(payload['user_id'])})

            if not current_user:
                return jsonify({'error': 'User not found'}), 401

            return f(current_user, *args, **kwargs)

        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401

    return decorated_function