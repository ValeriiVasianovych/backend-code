from flask import Blueprint, jsonify, request
from bson import ObjectId
from app.models.car import Car
from app.utils.auth_utils import token_required

cars_bp = Blueprint('cars', __name__)

@cars_bp.route('/cars', methods=['POST'])
@token_required
def create_car(current_user):
    data = request.get_json()
    if not all(k in data for k in ["brand", "model", "year", "price_per_day"]):
        return jsonify({"error": "Missing required fields"}), 400
    
    result = Car.create(data)
    return jsonify({"message": "Car created successfully", "id": str(result.inserted_id)}), 201

@cars_bp.route('/cars', methods=['GET'])
@token_required
def get_cars(current_user):
    cars = Car.get_all()
    # Convert ObjectId to string for JSON serialization
    for car in cars:
        car['_id'] = str(car['_id'])
    return jsonify(cars)

@cars_bp.route('/cars/<car_id>', methods=['GET'])
@token_required
def get_car(current_user, car_id):
    try:
        car = Car.get_by_id(ObjectId(car_id))
        if car:
            car['_id'] = str(car['_id'])
            return jsonify(car)
        return jsonify({"error": "Car not found"}), 404
    except:
        return jsonify({"error": "Invalid car ID"}), 400

@cars_bp.route('/cars/<car_id>', methods=['PUT'])
@token_required
def update_car(current_user, car_id):
    try:
        data = request.get_json()
        result = Car.update(ObjectId(car_id), data)
        if result.modified_count:
            return jsonify({"message": "Car updated successfully"})
        return jsonify({"error": "Car not found"}), 404
    except:
        return jsonify({"error": "Invalid car ID"}), 400

@cars_bp.route('/cars/<car_id>', methods=['DELETE'])
@token_required
def delete_car(current_user, car_id):
    try:
        result = Car.delete(ObjectId(car_id))
        if result.deleted_count:
            return jsonify({"message": "Car deleted successfully"})
        return jsonify({"error": "Car not found"}), 404
    except:
        return jsonify({"error": "Invalid car ID"}), 400 