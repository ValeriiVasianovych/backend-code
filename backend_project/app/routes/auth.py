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
from app.controllers.auth_controller import AuthController

auth_bp = Blueprint('auth', __name__)
auth_service = AuthService()
github_service = GitHubService()
logger = logging.getLogger(__name__)
auth_controller = AuthController()

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
    return auth_controller.register()

@auth_bp.route('/login', methods=['POST'])
def login():
    return auth_controller.login()

@auth_bp.route('/refresh', methods=['POST'])
def refresh_token():
    return auth_controller.refresh_token()

@auth_bp.route('/users', methods=['GET'])
@token_required
def get_users(current_user):
    return auth_controller.get_users(current_user)

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
        
        return redirect(url_for('rentals.cars_page', 
            access_token=tokens['access_token'],
            refresh_token=tokens['refresh_token']))
        
    except Exception as e:
        logger.error(f"GitHub callback error: {str(e)}")
        return redirect(url_for('main.index', message=str(e)))