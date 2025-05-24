from flask import Blueprint, jsonify, request, render_template
from app.extensions import mongo
from app.utils.decorators import token_required
from bson import ObjectId
from datetime import datetime

rentals_bp = Blueprint('rentals', __name__)

@rentals_bp.route('/cars', methods=['GET'])
def cars_page():
    return render_template('cars.html')

@rentals_bp.route('/cars', methods=['GET'])
@token_required
def get_cars(current_user):
    try:
        cars = list(mongo.db.cars.find())
        for car in cars:
            car['_id'] = str(car['_id'])
        return jsonify({'cars': cars}), 200
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@rentals_bp.route('/cars', methods=['POST'])
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
        
        optional_fields = [
            'vin', 'features', 'location', 'rental_price_per_hour',
            'min_rental_period', 'max_rental_period',
            'availability_schedule', 'deposit_amount',
            'insurance_included', 'mileage_limit_per_day',
            'extra_mileage_fee', 'owner_id'
        ]
        
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields', 'required_fields': required_fields}), 400
            
        car = {
            # Основная информация
            'brand': data['brand'],
            'model': data['model'],
            'year': data['year'],
            'color': data['color'],
            'body_type': data['body_type'],
            'seats': data['seats'],
            'doors': data['doors'],
            'transmission': data['transmission'],
            'fuel_type': data['fuel_type'],
            'engine_volume': data['engine_volume'],
            'engine_power': data['engine_power'],
            'mileage': data['mileage'],
            
            # Доступность и аренда
            'available': data['available'],
            'rental_price_per_day': data['rental_price_per_day'],
            
            # Дополнительные поля (опциональные)
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        
        # Добавляем опциональные поля, если они предоставлены
        for field in optional_fields:
            if field in data:
                car[field] = data[field]
        
        result = mongo.db.cars.insert_one(car)
        car['_id'] = str(result.inserted_id)
        
        return jsonify({'message': 'Car added successfully', 'car': car}), 201
        
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@rentals_bp.route('/cars/<car_id>', methods=['PUT'])
@token_required
def update_car(current_user, car_id):
    try:
        data = request.get_json()
        car = mongo.db.cars.find_one({'_id': ObjectId(car_id)})
        
        if not car:
            return jsonify({'error': 'Car not found'}), 404
            
        allowed_fields = [
            'brand', 'model', 'year', 'color', 'body_type',
            'seats', 'doors', 'transmission', 'fuel_type',
            'engine_volume', 'engine_power', 'mileage',
            'rental_price_per_day', 'available', 'vin',
            'features', 'location', 'rental_price_per_hour',
            'min_rental_period', 'max_rental_period',
            'availability_schedule', 'deposit_amount',
            'insurance_included', 'mileage_limit_per_day',
            'extra_mileage_fee', 'owner_id'
        ]
        
        update_data = {}
        for field in allowed_fields:
            if field in data:
                update_data[field] = data[field]
        
        if update_data:
            update_data['updated_at'] = datetime.utcnow()
            mongo.db.cars.update_one(
                {'_id': ObjectId(car_id)},
                {'$set': update_data}
            )
            
        updated_car = mongo.db.cars.find_one({'_id': ObjectId(car_id)})
        updated_car['_id'] = str(updated_car['_id'])
        
        return jsonify({'message': 'Car updated successfully', 'car': updated_car}), 200
        
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@rentals_bp.route('/cars/<car_id>', methods=['GET'])
@token_required
def get_car(current_user, car_id):
    try:
        car = mongo.db.cars.find_one({'_id': ObjectId(car_id)})
        if not car:
            return jsonify({'error': 'Car not found'}), 404
            
        car['_id'] = str(car['_id'])
        return jsonify({'car': car}), 200
        
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@rentals_bp.route('/cars/<car_id>', methods=['DELETE'])
@token_required
def delete_car(current_user, car_id):
    try:
        result = mongo.db.cars.delete_one({'_id': ObjectId(car_id)})
        
        if result.deleted_count == 0:
            return jsonify({'error': 'Car not found'}), 404
            
        return jsonify({'message': 'Car deleted successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500