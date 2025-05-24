import requests
from flask import current_app
from app.extensions import mongo
from datetime import datetime
from bson import ObjectId

class GitHubService:
    @staticmethod
    def get_github_auth_url():
        client_id = current_app.config['GITHUB_CLIENT_ID']
        redirect_uri = current_app.config['GITHUB_REDIRECT_URI']
        return f"https://github.com/login/oauth/authorize?client_id={client_id}&redirect_uri={redirect_uri}&scope=user:email"

    @staticmethod
    def get_github_token(code):
        client_id = current_app.config['GITHUB_CLIENT_ID']
        client_secret = current_app.config['GITHUB_CLIENT_SECRET']
        redirect_uri = current_app.config['GITHUB_REDIRECT_URI']
        
        response = requests.post(
            'https://github.com/login/oauth/access_token',
            data={
                'client_id': client_id,
                'client_secret': client_secret,
                'code': code,
                'redirect_uri': redirect_uri
            },
            headers={'Accept': 'application/json'}
        )
        
        if response.status_code == 200:
            return response.json().get('access_token')
        return None

    @staticmethod
    def get_github_user(access_token):
        response = requests.get(
            'https://api.github.com/user',
            headers={
                'Authorization': f'token {access_token}',
                'Accept': 'application/json'
            }
        )
        
        if response.status_code == 200:
            return response.json()
        return None

    @staticmethod
    def get_github_emails(access_token):
        response = requests.get(
            'https://api.github.com/user/emails',
            headers={
                'Authorization': f'token {access_token}',
                'Accept': 'application/json'
            }
        )
        
        if response.status_code == 200:
            return response.json()
        return []

    @staticmethod
    def create_or_update_user(github_user, emails):
        primary_email = next((email['email'] for email in emails if email['primary']), None)
        if not primary_email:
            return None

        user = mongo.db.users.find_one({'email': primary_email})
        
        if not user:
            user = {
                'email': primary_email,
                'github_id': github_user['id'],
                'username': github_user['login'],
                'name': github_user.get('name', ''),
                'avatar_url': github_user.get('avatar_url', ''),
                'created_at': datetime.utcnow(),
                'is_active': True
            }
            result = mongo.db.users.insert_one(user)
            user['_id'] = result.inserted_id
        else:
            # Update existing user with latest GitHub data
            mongo.db.users.update_one(
                {'_id': user['_id']},
                {
                    '$set': {
                        'github_id': github_user['id'],
                        'username': github_user['login'],
                        'name': github_user.get('name', ''),
                        'avatar_url': github_user.get('avatar_url', '')
                    }
                }
            )
            user = mongo.db.users.find_one({'_id': user['_id']})

        return user 