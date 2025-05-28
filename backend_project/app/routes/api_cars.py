from flask import Blueprint, jsonify, request
from bson import ObjectId
from app.models.car import Car
from app.utils.decorators import token_required

api_cars_bp = Blueprint('api_cars', __name__, url_prefix='/api')

@api_cars_bp.route('/cars', methods=['POST'])
@token_required
def create_car(current_user):
    data = request.get_json()
    if not all(k in data for k in ["brand", "model", "year", "price_per_day"]):
        return jsonify({"error": "Missing required fields"}), 400
    
    result = Car.create(data, owner_id=current_user['_id'])
    return jsonify({"message": "Car created successfully", "id": str(result.inserted_id)}), 201

@api_cars_bp.route('/cars', methods=['GET'])
@token_required
def get_cars(current_user):
    cars = Car.get_all()
    for car in cars:
        car['_id'] = str(car['_id'])
        if 'owner_id' in car:
            car['owner_id'] = str(car['owner_id'])
    return jsonify(cars)

@api_cars_bp.route('/cars/my', methods=['GET'])
@token_required
def get_my_cars(current_user):
    cars = Car.get_by_owner(current_user['_id'])
    for car in cars:
        car['_id'] = str(car['_id'])
        if 'owner_id' in car:
            car['owner_id'] = str(car['owner_id'])
    return jsonify(cars)

@api_cars_bp.route('/cars/<car_id>', methods=['GET'])
@token_required
def get_car(current_user, car_id):
    try:
        car = Car.get_by_id(ObjectId(car_id))
        if car:
            car['_id'] = str(car['_id'])
            if 'owner_id' in car:
                car['owner_id'] = str(car['owner_id'])
            return jsonify(car)
        return jsonify({"error": "Car not found"}), 404
    except:
        return jsonify({"error": "Invalid car ID"}), 400

@api_cars_bp.route('/cars/<car_id>', methods=['PUT'])
@token_required
def update_car(current_user, car_id):
    try:
        car = Car.get_by_id(ObjectId(car_id))
        if not car:
            return jsonify({"error": "Car not found"}), 404
            
        # Check if user is the owner of the car
        if str(car.get('owner_id')) != str(current_user['_id']):
            return jsonify({"error": "Unauthorized to update this car"}), 403
            
        data = request.get_json()
        result = Car.update(ObjectId(car_id), data)
        if result.modified_count:
            return jsonify({"message": "Car updated successfully"})
        return jsonify({"error": "Car not found"}), 404
    except:
        return jsonify({"error": "Invalid car ID"}), 400

@api_cars_bp.route('/cars/<car_id>', methods=['DELETE'])
@token_required
def delete_car(current_user, car_id):
    try:
        car = Car.get_by_id(ObjectId(car_id))
        if not car:
            return jsonify({"error": "Car not found"}), 404
            
        # Check if user is the owner of the car
        if str(car.get('owner_id')) != str(current_user['_id']):
            return jsonify({"error": "Unauthorized to delete this car"}), 403
            
        result = Car.delete(ObjectId(car_id))
        if result.deleted_count:
            return jsonify({"message": "Car deleted successfully"})
        return jsonify({"error": "Car not found"}), 404
    except:
        return jsonify({"error": "Invalid car ID"}), 400 