from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import mongo
import datetime

class User:
    @staticmethod
    def create(data):
        hashed_password = generate_password_hash(data["password"]) if data.get("password") else None
        user_data = {
            "username": data["username"],
            "email": data["email"],
            "first_name": data.get("first_name"),
            "last_name": data.get("last_name"),
            "password": hashed_password,
            "github_id": data.get("github_id"),
            "created_at": datetime.datetime.utcnow(),
            "refresh_tokens": [],
            "github_access_token": data.get("github_access_token")
        }
        return mongo.db.users.insert_one(user_data)

    @staticmethod
    def find_by_username(username):
        return mongo.db.users.find_one({"username": username})

    @staticmethod
    def find_by_email(email):
        return mongo.db.users.find_one({"email": email})

    @staticmethod
    def find_by_github_id(github_id):
        return mongo.db.users.find_one({"github_id": github_id})

    @staticmethod
    def find_by_id(user_id):
        return mongo.db.users.find_one({"_id": user_id})

    @staticmethod
    def update_github_token(username, access_token):
        mongo.db.users.update_one(
            {"username": username},
            {"$set": {"github_access_token": access_token}}
        )

    @staticmethod
    def add_refresh_token(username, token):
        mongo.db.users.update_one(
            {"username": username},
            {"$push": {"refresh_tokens": token}}
        )

    @staticmethod
    def get_all_users():
        return list(mongo.db.users.find({}, {"password": 0, "refresh_tokens": 0, "google_access_token": 0}))
    
    @staticmethod
    def delete_user(username):
        result = mongo.db.users.delete_one({"username": username})
        return result

    @staticmethod
    def delete_user_by_id(user_id):
        result = mongo.db.users.delete_one({"_id": user_id})
        return result