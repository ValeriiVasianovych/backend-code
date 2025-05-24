from flask import jsonify
from app.models.rental import Rental
from app.utils.validators import validate_rental_data

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