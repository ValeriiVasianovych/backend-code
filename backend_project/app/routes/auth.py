from flask import Blueprint, request, jsonify, render_template, redirect, url_for, session
from app.extensions import mongo
from app.services.auth_service import AuthService
from app.services.github_service import GitHubService
from app.utils.decorators import token_required
from app.utils.validators import validate_email, validate_password
from app.utils.error_handlers import ServiceError
import jwt
from app.config import Config
from bson import ObjectId
import logging

auth_bp = Blueprint('auth', __name__)
auth_service = AuthService()
github_service = GitHubService()
logger = logging.getLogger(__name__)

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
        except Exception as e:
            logger.error(f"Error getting current user: {str(e)}")
            return None
    return None

@auth_bp.route('/login', methods=['GET'])
def login_page():
    current_user = get_current_user()
    if current_user:
        return redirect(url_for('main.index'))
    return render_template('login.html')

@auth_bp.route('/register', methods=['GET'])
def register_page():
    current_user = get_current_user()
    if current_user:
        return redirect(url_for('main.index'))
    return render_template('register.html')

@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided', 'status': 'error'}), 400

        email = data.get('email')
        password = data.get('password')
        
        # Input validation
        if not all([email, password]):
            return jsonify({'error': 'Required fields are missing', 'status': 'error'}), 400
            
        if not validate_email(email):
            return jsonify({'error': 'Invalid email format', 'status': 'error'}), 400
            
        if not validate_password(password):
            return jsonify({'error': 'Password does not meet security requirements', 'status': 'error'}), 400
            
        user = auth_service.create_user(email, password)
        tokens = auth_service.generate_tokens(user['_id'])
        
        # Redirect to cars page with tokens
        return redirect(url_for('rentals.cars_page', 
            access_token=tokens['access_token'],
            refresh_token=tokens['refresh_token']))
        
    except ValueError as e:
        return jsonify({'error': str(e), 'status': 'error'}), 400
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        return jsonify({'error': 'Internal server error', 'status': 'error'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided', 'status': 'error'}), 400

        email = data.get('email')
        password = data.get('password')
        
        if not all([email, password]):
            return jsonify({'error': 'Required fields are missing', 'status': 'error'}), 400
            
        user = auth_service.get_user_by_email(email)
        if not user:
            return jsonify({'error': 'Invalid email or password', 'status': 'error'}), 401
            
        if not auth_service.verify_password(password, user['password']):
            return jsonify({'error': 'Invalid email or password', 'status': 'error'}), 401
            
        tokens = auth_service.generate_tokens(user['_id'])
        
        # Redirect to cars page with tokens
        return redirect(url_for('rentals.cars_page', 
            access_token=tokens['access_token'],
            refresh_token=tokens['refresh_token']))
        
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return jsonify({'error': 'Internal server error', 'status': 'error'}), 500

@auth_bp.route('/refresh', methods=['POST'])
def refresh_token():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided', 'status': 'error'}), 400

        refresh_token = data.get('refresh_token')
        
        if not refresh_token:
            return jsonify({'error': 'Refresh token is missing', 'status': 'error'}), 400
            
        try:
            payload = jwt.decode(refresh_token, Config.JWT_SECRET_KEY, algorithms=['HS256'])
            user_id = ObjectId(payload['user_id'])
            
            user = mongo.db.users.find_one({'_id': user_id})
            if not user:
                return jsonify({'error': 'User not found', 'status': 'error'}), 401
                
            tokens = auth_service.generate_tokens(user_id)
            return jsonify({
                'message': 'Token refreshed successfully',
                'status': 'success',
                'tokens': tokens
            }), 200
            
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Refresh token has expired', 'status': 'error'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid refresh token', 'status': 'error'}), 401
        except Exception as e:
            logger.error(f"Token refresh error: {str(e)}")
            return jsonify({'error': 'Invalid token format', 'status': 'error'}), 401
            
    except Exception as e:
        logger.error(f"Refresh token error: {str(e)}")
        return jsonify({'error': 'Internal server error', 'status': 'error'}), 500

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
            'users': users,
            'status': 'success'
        }), 200
        
    except Exception as e:
        logger.error(f"Get users error: {str(e)}")
        return jsonify({'error': 'Internal server error', 'status': 'error'}), 500

@auth_bp.route('/github-login')
def github_login():
    try:
        auth_url, state = github_service.get_authorization_url()
        session['oauth_state'] = state
        return redirect(auth_url)
    except Exception as e:
        logger.error(f"GitHub login error: {str(e)}")
        return redirect(url_for('main.index', message='GitHub login failed'))

@auth_bp.route('/github-callback')
def github_callback():
    if 'error' in request.args:
        return redirect(url_for('main.index', message='GitHub login was cancelled'))
        
    state = request.args.get('state')
    stored_state = session.pop('oauth_state', None)
    
    if not state or state != stored_state:
        return redirect(url_for('main.index', message='OAuth state verification failed'))
        
    code = request.args.get('code')
    if not code:
        return redirect(url_for('main.index', message='No authorization code provided'))
        
    try:
        access_token = github_service.get_access_token(code)
        github_data = github_service.get_user_data(access_token)
        user = github_service.create_or_update_user(github_data, access_token)
        tokens = auth_service.generate_tokens(user['_id'])
        
        # Redirect to cars page with tokens
        return redirect(url_for('rentals.cars_page', 
            access_token=tokens['access_token'],
            refresh_token=tokens['refresh_token']))
        
    except Exception as e:
        logger.error(f"GitHub callback error: {str(e)}")
        return redirect(url_for('main.index', message=str(e)))

@auth_bp.route('/change-password', methods=['POST'])
@token_required
def change_password(current_user):
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided', 'status': 'error'}), 400

        current_password = data.get('current_password')
        new_password = data.get('new_password')
        
        if not all([current_password, new_password]):
            return jsonify({'error': 'Required fields are missing', 'status': 'error'}), 400
            
        auth_service.change_password(current_user['_id'], current_password, new_password)
        
        return jsonify({
            'message': 'Password changed successfully',
            'status': 'success'
        }), 200
        
    except ValueError as e:
        return jsonify({'error': str(e), 'status': 'error'}), 400
    except Exception as e:
        logger.error(f"Change password error: {str(e)}")
        return jsonify({'error': 'Internal server error', 'status': 'error'}), 500