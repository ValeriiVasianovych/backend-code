from flask import Blueprint, jsonify, request
from app.models.user import User
from bson import ObjectId

users_bp = Blueprint('users', __name__)

@users_bp.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    if not all(k in data for k in ["username", "email", "password"]):
        return jsonify({"error": "Missing required fields"}), 400
    
    if User.find_by_username(data["username"]):
        return jsonify({"error": "Username already exists"}), 400
    if User.find_by_email(data["email"]):
        return jsonify({"error": "Email already exists"}), 400
    
    result = User.create(data)
    return jsonify({"message": "User created successfully", "id": str(result.inserted_id)}), 201

@users_bp.route('/users', methods=['GET'])
def get_users():
    users = User.get_all_users()
    for user in users:
        user['_id'] = str(user['_id'])
    return jsonify(users)

@users_bp.route('/users/<user_id>', methods=['GET'])
def get_user(user_id):
    try:
        user = User.find_by_id(ObjectId(user_id))
        if user:
            user['_id'] = str(user['_id'])
            user.pop('password', None)
            user.pop('refresh_tokens', None)
            return jsonify(user)
        return jsonify({"error": "User not found"}), 404
    except:
        return jsonify({"error": "Invalid user ID"}), 400

@users_bp.route('/users/<user_id>', methods=['PUT'])
def update_user(user_id):
    try:
        data = request.get_json()
        data.pop('password', None)
        data.pop('refresh_tokens', None)
        
        user = User.find_by_id(ObjectId(user_id))
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        update_data = {k: v for k, v in data.items() if v is not None}
        mongo.db.users.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": update_data}
        )
        return jsonify({"message": "User updated successfully"})
    except:
        return jsonify({"error": "Invalid user ID"}), 400

@users_bp.route('/users/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    try:
        result = User.delete_user_by_id(ObjectId(user_id))
        if result.deleted_count:
            return jsonify({"message": "User deleted successfully"})
        return jsonify({"error": "User not found"}), 404
    except:
        return jsonify({"error": "Invalid user ID"}), 400 