from flask import Blueprint, request, jsonify, render_template, redirect, url_for
from app.extensions import mongo
from app.services.auth_service import AuthService
from app.utils.decorators import token_required
from app.utils.validators import validate_email, validate_password
import jwt
from app.config import Config
from bson import ObjectId

auth_bp = Blueprint('auth', __name__)
auth_service = AuthService()

@auth_bp.route('/login', methods=['GET'])
def login_page():
    # Check if user is already authenticated
    token = None
    if 'Authorization' in request.headers:
        auth_header = request.headers['Authorization']
        try:
            token = auth_header.split(" ")[1]
            data = jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=['HS256'])
            user_id = ObjectId(data['user_id'])
            user = mongo.db.users.find_one({'_id': user_id})
            if user:
                return redirect(url_for('main.index'))
        except:
            pass
    return render_template('login.html')

@auth_bp.route('/register', methods=['GET'])
def register_page():
    # Check if user is already authenticated
    token = None
    if 'Authorization' in request.headers:
        auth_header = request.headers['Authorization']
        try:
            token = auth_header.split(" ")[1]
            data = jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=['HS256'])
            user_id = ObjectId(data['user_id'])
            user = mongo.db.users.find_one({'_id': user_id})
            if user:
                return redirect(url_for('main.index'))
        except:
            pass
    return render_template('register.html')

@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        # Input validation
        if not all([email, password]):
            return jsonify({'error': 'Required fields are missing'}), 400
            
        if not validate_email(email):
            return jsonify({'error': 'Invalid email format'}), 400
            
        if not validate_password(password):
            return jsonify({'error': 'Password does not meet security requirements'}), 400
            
        user = auth_service.create_user(email, password)
        tokens = auth_service.generate_tokens(user['_id'])
        
        return jsonify({
            'message': 'User successfully registered',
            'tokens': tokens
        }), 201
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        if not all([email, password]):
            return jsonify({'error': 'Required fields are missing'}), 400
            
        user = auth_service.get_user_by_email(email)
        if not user or not auth_service.verify_password(password, user['password']):
            return jsonify({'error': 'Invalid email or password'}), 401
            
        tokens = auth_service.generate_tokens(user['_id'])
        return jsonify({'tokens': tokens}), 200
        
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@auth_bp.route('/refresh', methods=['POST'])
def refresh_token():
    try:
        data = request.get_json()
        refresh_token = data.get('refresh_token')
        
        if not refresh_token:
            return jsonify({'error': 'Refresh token is missing'}), 400
            
        try:
            payload = jwt.decode(refresh_token, Config.JWT_SECRET_KEY, algorithms=['HS256'])
            user_id = ObjectId(payload['user_id'])
            
            # Проверяем существование пользователя
            user = mongo.db.users.find_one({'_id': user_id})
            if not user:
                return jsonify({'error': 'User not found'}), 401
                
            tokens = auth_service.generate_tokens(user_id)
            return jsonify({'tokens': tokens}), 200
            
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Refresh token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid refresh token'}), 401
        except Exception as e:
            return jsonify({'error': 'Invalid token format'}), 401
            
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@auth_bp.route('/users', methods=['GET'])
@token_required
def get_users(current_user):
    try:
        # Get all users, excluding their passwords
        users = list(mongo.db.users.find({}, {'password': 0}))
        
        # Convert ObjectId to strings for JSON
        for user in users:
            user['_id'] = str(user['_id'])
            
        return jsonify({
            'users': users
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500