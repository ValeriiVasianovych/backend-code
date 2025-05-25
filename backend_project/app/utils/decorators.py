from functools import wraps
from flask import request, jsonify
import jwt
from app.config import Config
from app.extensions import mongo
from bson import ObjectId

def get_current_user():
    token = None
    if 'Authorization' in request.headers:
        auth_header = request.headers['Authorization']
        try:
            token = auth_header.split(" ")[1]
            data = jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=['HS256'])
            user_id = ObjectId(data['user_id'])
            current_user = mongo.db.users.find_one({'_id': user_id})
            return current_user
        except:
            return None
    return None

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        current_user = get_current_user()
        if not current_user:
            return jsonify({'error': 'Authentication required'}), 401
        return f(current_user, *args, **kwargs)
    return decorated