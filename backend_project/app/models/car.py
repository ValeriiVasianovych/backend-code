from app.extensions import mongo
import datetime
from .base_model import BaseModel
from bson import ObjectId

class Car(BaseModel):
    collection_name = 'cars'

    @classmethod
    def get_available_cars(cls):
        return cls.find_all({'available': True})

    @classmethod
    def update_availability(cls, car_id, available):
        return cls.update(car_id, {'available': available})

    @classmethod
    def get_car_by_id(cls, car_id):
        return cls.find_by_id(car_id)

    @classmethod
    def get_cars_by_filters(cls, filters=None):
        if filters is None:
            filters = {}
        return cls.find_all(filters)

    @staticmethod
    def create(data, owner_id=None):
        car_data = {
            "brand": data["brand"],
            "model": data["model"],
            "year": data["year"],
            "price_per_day": data["price_per_day"],
            "available": data.get("available", True),
            "transmission": data.get("transmission", "Automatic"),
            "fuel_type": data.get("fuel_type", "Petrol"),
            "engine": data.get("engine", "2.0L"),
            "mileage": data.get("mileage", 0),
            "seats": data.get("seats", 5),
            "doors": data.get("doors", 4),
            "created_at": datetime.datetime.utcnow(),
            "owner_id": ObjectId(owner_id) if owner_id else None
        }
        return mongo.db.cars.insert_one(car_data)

    @staticmethod
    def get_all():
        return list(mongo.db.cars.find())

    @staticmethod
    def get_by_id(car_id):
        return mongo.db.cars.find_one({"_id": car_id})

    @staticmethod
    def get_by_owner(owner_id):
        return list(mongo.db.cars.find({"owner_id": ObjectId(owner_id)}))

    @staticmethod
    def update(car_id, data):
        update_data = {k: v for k, v in data.items() if v is not None}
        return mongo.db.cars.update_one(
            {"_id": car_id},
            {"$set": update_data}
        )

    @staticmethod
    def delete(car_id):
        return mongo.db.cars.delete_one({"_id": car_id}) 