from werkzeug.security import generate_password_hash, check_password_hash
from .base_model import BaseModel
from datetime import datetime

class User(BaseModel):
    collection_name = 'users'

    @classmethod
    def create(cls, data):
        if "password" in data:
            data["password"] = generate_password_hash(data["password"])
        return super().create(data)

    @classmethod
    def find_by_email(cls, email):
        return cls.get_collection().find_one({"email": email})

    @classmethod
    def find_by_github_id(cls, github_id):
        return cls.get_collection().find_one({"github_id": github_id})

    @classmethod
    def verify_password(cls, password, hashed_password):
        return check_password_hash(hashed_password, password)

    @classmethod
    def update_github_token(cls, user_id, access_token):
        return cls.update(user_id, {"github_access_token": access_token})

    @classmethod
    def add_refresh_token(cls, user_id, token):
        return cls.get_collection().update_one(
            {"_id": user_id},
            {"$push": {"refresh_tokens": token}}
        )

    @classmethod
    def get_all_users(cls):
        return list(cls.get_collection().find(
            {},
            {"password": 0, "refresh_tokens": 0, "github_access_token": 0}
        ))

    @classmethod
    def find_by_username(cls, username):
        return cls.get_collection().find_one({"username": username})

    @classmethod
    def find_by_id(cls, user_id):
        return cls.get_collection().find_one({"_id": user_id})

    @classmethod
    def delete_user(cls, username):
        result = cls.get_collection().delete_one({"username": username})
        return result

    @classmethod
    def delete_user_by_id(cls, user_id):
        result = cls.get_collection().delete_one({"_id": user_id})
        return result