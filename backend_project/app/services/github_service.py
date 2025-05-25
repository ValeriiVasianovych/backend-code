import requests
from app.config import Config
from app.extensions import mongo
from app.utils.error_handlers import ServiceError
import secrets

class GitHubService:
    @staticmethod
    def get_authorization_url():
        state = secrets.token_hex(16)
        params = {
            'client_id': Config.GITHUB_CLIENT_ID,
            'redirect_uri': Config.GITHUB_CALLBACK_URL,
            'scope': 'user:email,read:user',
            'state': state
        }
        return f"https://github.com/login/oauth/authorize?{'&'.join(f'{k}={v}' for k, v in params.items())}", state

    @staticmethod
    def get_access_token(code):
        response = requests.post(
            'https://github.com/login/oauth/access_token',
            data={
                'client_id': Config.GITHUB_CLIENT_ID,
                'client_secret': Config.GITHUB_CLIENT_SECRET,
                'code': code,
                'redirect_uri': Config.GITHUB_CALLBACK_URL
            },
            headers={'Accept': 'application/json'}
        )
        
        if response.status_code != 200:
            raise ServiceError('Failed to get access token from GitHub', 400)
            
        data = response.json()
        if 'error' in data:
            raise ServiceError(f"GitHub error: {data['error_description']}", 400)
            
        return data['access_token']

    @staticmethod
    def get_user_data(access_token):
        headers = {'Authorization': f'token {access_token}'}
        response = requests.get('https://api.github.com/user', headers=headers)
        
        if response.status_code != 200:
            raise ServiceError('Failed to get user data from GitHub', 400)
            
        user_data = response.json()
        
        # Get user email
        email_response = requests.get('https://api.github.com/user/emails', headers=headers)
        if email_response.status_code == 200:
            emails = email_response.json()
            primary_email = next((email['email'] for email in emails if email['primary']), None)
            if primary_email:
                user_data['email'] = primary_email
        
        return user_data

    @staticmethod
    def create_or_update_user(github_data, access_token):
        user = {
            'github_id': github_data['id'],
            'email': github_data.get('email'),
            'name': github_data.get('name'),
            'login': github_data.get('login'),
            'avatar_url': github_data.get('avatar_url'),
            'github_access_token': access_token
        }
        
        existing_user = mongo.db.users.find_one({'github_id': github_data['id']})
        if existing_user:
            mongo.db.users.update_one(
                {'github_id': github_data['id']},
                {'$set': user}
            )
            user['_id'] = existing_user['_id']
        else:
            result = mongo.db.users.insert_one(user)
            user['_id'] = result.inserted_id
            
        return user 