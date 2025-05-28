from flask import Blueprint, jsonify, request, render_template
from app.extensions import mongo
from app.utils.decorators import token_required
from bson import ObjectId
from datetime import datetime
from app.services.rental_service import RentalService

rentals_bp = Blueprint('rentals', __name__)

@rentals_bp.route('/cars/page', methods=['GET'])
def cars_page():
    try:
        access_token = request.args.get('access_token')
        refresh_token = request.args.get('refresh_token')
        
        cars = list(mongo.db.cars.find({'available': True}))
        for car in cars:
            car['_id'] = str(car['_id'])
            
        return render_template('cars.html', 
            cars=cars,
            access_token=access_token,
            refresh_token=refresh_token)
    except Exception as e:
        return render_template('cars.html', cars=[])

@rentals_bp.route('/api/cars', methods=['GET'])
@token_required
def get_cars():
    try:
        return RentalService.get_all_cars()
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@rentals_bp.route('/api/cars', methods=['POST'])
@token_required
def add_car(current_user):
    try:
        data = request.get_json()
        required_fields = [
            'brand', 'model', 'year', 'color', 'body_type', 
            'seats', 'doors', 'transmission', 'fuel_type',
            'engine_volume', 'engine_power', 'mileage',
            'rental_price_per_day', 'available'
        ]
        
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields', 'required_fields': required_fields}), 400
            
        return RentalService.add_car(data)
        
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@rentals_bp.route('/api/cars/<car_id>', methods=['PUT'])
@token_required
def update_car(current_user, car_id):
    try:
        if not ObjectId.is_valid(car_id):
            return jsonify({'error': 'Invalid car ID format'}), 400
            
        data = request.get_json()
        return RentalService.update_car(car_id, data)
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@rentals_bp.route('/api/cars/<car_id>', methods=['GET'])
def get_car(car_id):
    try:
        if not ObjectId.is_valid(car_id):
            return jsonify({'error': 'Invalid car ID format'}), 400
            
        car = mongo.db.cars.find_one({'_id': ObjectId(car_id)})
        if not car:
            return jsonify({'error': 'Car not found'}), 404
            
        car['_id'] = str(car['_id'])
        return jsonify({'car': car}), 200
        
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@rentals_bp.route('/api/cars/<car_id>', methods=['DELETE'])
@token_required
def delete_car(current_user, car_id):
    try:
        if not ObjectId.is_valid(car_id):
            return jsonify({'error': 'Invalid car ID format'}), 400
            
        return RentalService.delete_car(car_id)
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500