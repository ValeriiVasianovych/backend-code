from flask import Blueprint, render_template
from app.utils.decorators import token_required
from functools import wraps
from flask import request, jsonify
import jwt
from app.config import Config
from app.extensions import mongo
from bson import ObjectId

main_bp = Blueprint('main', __name__)

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

@main_bp.route('/')
def index():
    current_user = get_current_user()
    return render_template('index.html', current_user=current_user)


# {
#     "email": "asdsad@asfafa.com",
#     "password": "affafs2Sdddd@"
# }