from app.extensions import mongo
import datetime

class Car:
    @staticmethod
    def create(data):
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
            "created_at": datetime.datetime.utcnow()
        }
        return mongo.db.cars.insert_one(car_data)

    @staticmethod
    def get_all():
        return list(mongo.db.cars.find())

    @staticmethod
    def get_by_id(car_id):
        return mongo.db.cars.find_one({"_id": car_id})

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