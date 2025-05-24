from flask import Blueprint, request, jsonify, render_template, redirect, url_for
from app.extensions import mongo
from app.services.auth_service import AuthService
from app.services.github_service import GitHubService
from app.utils.decorators import token_required
from app.utils.validators import validate_email, validate_password
import jwt
from app.config import Config
from bson import ObjectId
import logging
import traceback

auth_bp = Blueprint('auth', __name__)
auth_service = AuthService()
github_service = GitHubService()
logger = logging.getLogger(__name__)

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
        if not user:
            logger.error(f"User not found for email: {email}")
            return jsonify({'error': 'Invalid email or password'}), 401
            
        if not auth_service.verify_password(password, user['password']):
            logger.error(f"Invalid password for user: {email}")
            return jsonify({'error': 'Invalid email or password'}), 401
            
        try:
            tokens = auth_service.generate_tokens(user['_id'])
            logger.info(f"Successfully generated tokens for user: {email}")
            return jsonify({'tokens': tokens}), 200
        except Exception as token_error:
            logger.error(f"Token generation error: {str(token_error)}")
            logger.error(f"Token error traceback: {traceback.format_exc()}")
            return jsonify({'error': 'Token generation failed'}), 500
        
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        logger.error(f"Login error traceback: {traceback.format_exc()}")
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

@auth_bp.route('/current-user', methods=['GET'])
@token_required
def get_current_user(current_user):
    try:
        # Remove sensitive data
        if 'password' in current_user:
            del current_user['password']
            
        # Convert ObjectId to string
        current_user['_id'] = str(current_user['_id'])
        
        return jsonify(current_user), 200
        
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@auth_bp.route('/github-login')
def github_login():
    """Redirect to GitHub OAuth page"""
    return redirect(github_service.get_github_auth_url())

@auth_bp.route('/github-callback')
def github_callback():
    """Handle GitHub OAuth callback"""
    try:
        code = request.args.get('code')
        if not code:
            return jsonify({'error': 'No code provided'}), 400

        # Get access token
        access_token = github_service.get_github_token(code)
        if not access_token:
            return jsonify({'error': 'Failed to get access token'}), 400

        # Get user info from GitHub
        github_user = github_service.get_github_user(access_token)
        if not github_user:
            return jsonify({'error': 'Failed to get user info'}), 400

        # Get user emails
        emails = github_service.get_github_emails(access_token)
        if not emails:
            return jsonify({'error': 'Failed to get user emails'}), 400

        # Create or update user
        user = github_service.create_or_update_user(github_user, emails)
        if not user:
            return jsonify({'error': 'Failed to create/update user'}), 400

        # Generate JWT tokens
        tokens = auth_service.generate_tokens(user['_id'])
        
        # Render template with tokens
        return render_template('github_callback.html', tokens=tokens)
        
    except Exception as e:
        logger.error(f"GitHub callback error: {str(e)}")
        logger.error(f"GitHub callback error traceback: {traceback.format_exc()}")
        return jsonify({'error': 'Internal server error'}), 500