from flask import request, render_template
from app.controllers.base_controller import BaseController
from app.models.car import Car
from app.utils.error_handlers import ServiceError
import logging

logger = logging.getLogger(__name__)

class CarController(BaseController):
    def get_cars_page(self):
        try:
            access_token = request.args.get('access_token')
            refresh_token = request.args.get('refresh_token')
            
            cars = Car.get_available_cars()
            for car in cars:
                car['_id'] = str(car['_id'])
                
            return render_template('cars.html', 
                cars=cars,
                access_token=access_token,
                refresh_token=refresh_token)
        except Exception as e:
            logger.error(f"Error getting cars page: {str(e)}")
            return render_template('cars.html', cars=[])

    def get_car(self, car_id):
        try:
            car = Car.get_car_by_id(car_id)
            if car:
                car['_id'] = str(car['_id'])
                return self.success_response(data={'car': car})
            return self.error_response("Car not found", 404)
        except Exception as e:
            logger.error(f"Error getting car: {str(e)}")
            return self.error_response("Internal server error", 500)

    def update_car_availability(self, car_id, available):
        try:
            if Car.update_availability(car_id, available):
                return self.success_response(message="Car availability updated successfully")
            return self.error_response("Car not found", 404)
        except Exception as e:
            logger.error(f"Error updating car availability: {str(e)}")
            return self.error_response("Internal server error", 500)

    def get_filtered_cars(self):
        try:
            filters = {}
            
            brand = request.args.get('brand')
            transmission = request.args.get('transmission')
            fuel_type = request.args.get('fuel_type')
            min_price = request.args.get('min_price')
            max_price = request.args.get('max_price')
            
            if brand:
                filters['brand'] = brand
            if transmission:
                filters['transmission'] = transmission
            if fuel_type:
                filters['fuel_type'] = fuel_type
            if min_price or max_price:
                filters['price_per_day'] = {}
                if min_price:
                    filters['price_per_day']['$gte'] = float(min_price)
                if max_price:
                    filters['price_per_day']['$lte'] = float(max_price)
            
            cars = Car.get_cars_by_filters(filters)
            for car in cars:
                car['_id'] = str(car['_id'])
                
            return self.success_response(data={'cars': cars})
        except Exception as e:
            logger.error(f"Error getting filtered cars: {str(e)}")
            return self.error_response("Internal server error", 500) 