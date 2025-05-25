from flask import jsonify
from app.models.rental import Rental
from app.utils.validators import validate_rental_data
from app.extensions import mongo
from bson import ObjectId
from datetime import datetime

class RentalService:
    @staticmethod
    def get_all():
        rentals = Rental.get_all()
        return jsonify(rentals), 200

    @staticmethod
    def get_by_id(rental_id):
        rental = Rental.find_by_id(rental_id)
        if rental:
            return jsonify(rental), 200
        return jsonify({"error": "Rental not found"}), 404

    @staticmethod
    def create(data):
        valid, message = validate_rental_data(data)
        if not valid:
            return jsonify({"error": message}), 400
        
        if Rental.find_by_id(data["rental_id"]):
            return jsonify({"error": "Rental ID already exists"}), 409
            
        Rental.create(data)
        return jsonify({"message": "Rental created successfully"}), 201

    @staticmethod
    def update(rental_id, data, method):
        if "rental_id" in data:
            return jsonify({"error": "Cannot modify rental_id"}), 400

        if method == "PATCH":
            for field in data:
                if field not in ["car_model", "car_brand", "car_year", "rental_price", "rental_duration", "additional_info"]:
                    return jsonify({"error": f"Invalid field: {field}"}), 400
        else:
            valid, message = validate_rental_data(data)
            if not valid:
                return jsonify({"error": message}), 400

        result = Rental.update(rental_id, data)
        if result.matched_count:
            return jsonify({"message": "Rental updated successfully"}), 200
        return jsonify({"error": "Rental not found"}), 404

    @staticmethod
    def delete(rental_id):
        result = Rental.delete(rental_id)
        if result.deleted_count:
            return jsonify({"message": "Rental deleted successfully"}), 200
        return jsonify({"error": "Rental not found"}), 404

    @staticmethod
    def add_car(car_data):
        try:
            car_data['created_at'] = datetime.utcnow()
            car_data['updated_at'] = datetime.utcnow()
            
            result = mongo.db.cars.insert_one(car_data)
            car_data['_id'] = str(result.inserted_id)
            
            return jsonify({
                'message': 'Car added successfully',
                'car': car_data
            }), 201
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @staticmethod
    def get_all_cars():
        try:
            cars = list(mongo.db.cars.find())
            for car in cars:
                car['_id'] = str(car['_id'])
            return jsonify({'cars': cars}), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @staticmethod
    def update_car(car_id, car_data):
        try:
            car = mongo.db.cars.find_one({'_id': ObjectId(car_id)})
            
            if not car:
                return jsonify({'error': 'Car not found'}), 404
                
            car_data['updated_at'] = datetime.utcnow()
            mongo.db.cars.update_one(
                {'_id': ObjectId(car_id)},
                {'$set': car_data}
            )
            
            updated_car = mongo.db.cars.find_one({'_id': ObjectId(car_id)})
            updated_car['_id'] = str(updated_car['_id'])
            
            return jsonify({
                'message': 'Car updated successfully',
                'car': updated_car
            }), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @staticmethod
    def delete_car(car_id):
        try:
            result = mongo.db.cars.delete_one({'_id': ObjectId(car_id)})
            
            if result.deleted_count == 0:
                return jsonify({'error': 'Car not found'}), 404
                
            return jsonify({'message': 'Car deleted successfully'}), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500