from flask import Flask, redirect, url_for, flash, request, render_template, g, session
from flask_github import GitHub
from pymongo import MongoClient
from dotenv import load_dotenv
import os
import secrets

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SECURE'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = 3600
app.config['SESSION_COOKIE_SAMESITE'] = 'Strict'
app.config['WTF_CSRF_ENABLED'] = True
app.config['WTF_CSRF_SECRET_KEY'] = secrets.token_hex(32)

@app.after_request
def add_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['Content-Security-Policy'] = "default-src 'self'"
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    return response

app.config['GITHUB_CLIENT_ID'] = os.getenv('GITHUB_CLIENT_ID')
app.config['GITHUB_CLIENT_SECRET'] = os.getenv('GITHUB_CLIENT_SECRET')

MONGO_URI = f"mongodb+srv://{os.getenv('DB_USERNAME')}:{os.getenv('DB_PASSWORD')}@flaskdb.2ttjd.mongodb.net/car_rental?retryWrites=true&w=majority&appName=FlaskDB"
try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    client.admin.command('ping')
    db = client['car_rental']
    users_collection = db['users']
except Exception as e:
    app.logger.error(f"Failed to connect to MongoDB: {e}")
    raise RuntimeError("Failed to connect to database. Please check your configuration.")

github = GitHub(app)

@github.access_token_getter
def get_github_token():
    user = g.get('user')
    return user.get('github_access_token') if user else None

@app.route('/')
def index():
    return render_template('index.html', user=g.get('user'))

@app.route('/login')
def login():
    if g.get('user'):
        return redirect(url_for('index'))
    session.clear()
    state = secrets.token_hex(16)
    session['oauth_state'] = state
    return github.authorize(scope='user:email,read:user,repo', state=state)

@app.route('/github-callback')
@github.authorized_handler
def authorized(oauth_token):
    next_url = request.args.get('next') or url_for('index')
    if oauth_token is None:
        flash('Authorization failed.', 'error')
        return redirect(next_url)

    state = request.args.get('state')
    stored_state = session.pop('oauth_state', None)
    
    if not state or state != stored_state:
        flash('OAuth state verification failed. Possible request forgery attack.', 'error')
        return redirect(url_for('index'))

    try:
        session['user_token'] = oauth_token
        g.user = {'github_access_token': oauth_token}
        
        # Get user data from GitHub
        user_data = github.get('user')
        if user_data is None:
            raise Exception("Failed to fetch user data from GitHub")
            
        user = {
            'github_access_token': oauth_token,
            'github_id': user_data['id'],
            'login': user_data['login'],
            'name': user_data.get('name'),
            'email': user_data.get('email'),
            'bio': user_data.get('bio') or 'No bio provided',
            'avatar_url': user_data.get('avatar_url')
        }

        existing_user = users_collection.find_one({'github_id': user_data['id']})
        if existing_user is None:
            users_collection.insert_one(user)
        else:
            users_collection.update_one(
                {'github_id': user_data['id']},
                {'$set': user}
            )

        g.user = user
        flash('Successfully logged in!', 'success')
        return redirect(next_url)
    except Exception as e:
        app.logger.error(f'Error during GitHub authorization: {str(e)}')
        session.pop('user_token', None)
        g.user = None
        flash('Error during authorization. Please try again.', 'error')
        return redirect(url_for('index'))

@app.route('/repo')
def repo():
    if not g.get('user'):
        flash('Please log in first.', 'error')
        return redirect(url_for('login'))
    
    try:
        repo_data = github.get('user/repos')
        if not repo_data:
            flash('No repositories found.', 'warning')
            return render_template('repo.html', repos=repo_data)  # Changed 'repos' instead of single 'repo'
        return render_template('repo.html', repos=repo_data)  # Changed 'repos' instead of single 'repo'
    except Exception as e:
        app.logger.error(f'GitHub API error: {str(e)}')
        flash('Error fetching repositories. Please try again later.', 'error')
        return redirect(url_for('index'))

@app.route('/logout')
def logout():
    if g.get('user'):
        users_collection.update_one(
            {'github_id': g.user['github_id']},
            {'$unset': {'github_access_token': ""}}
        )
    
    session.clear()
    g.user = None
    
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))

# Before request to load user
@app.before_request
def load_user():
    g.user = None
    token = session.get('user_token')
    if token:
        try:
            user = users_collection.find_one({'github_access_token': token})
            if user:
                g.user = user
        except Exception as e:
            app.logger.error(f'Error loading user from database: {str(e)}')
            session.pop('user_token', None)

@app.route('/api/profile')
def get_profile():
    if not g.get('user'):
        return {'error': 'Not authorized'}, 401
    
    user_data = {
        'github_id': g.user['github_id'],
        'login': g.user['login'],
        'name': g.user['name'],
        'email': g.user['email'],
        'bio': g.user['bio'],
        'avatar_url': g.user['avatar_url']
    }
    return user_data


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)