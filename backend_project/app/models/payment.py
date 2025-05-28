from app.extensions import mongo
import datetime
from .base_model import BaseModel

class Payment(BaseModel):
    collection_name = 'payments'

    @classmethod
    def create_payment(cls, data):
        payment_data = {
            "rental_id": data.get("rental_id"),
            "user_id": data["user_id"],
            "amount": data["amount"],
            "status": data.get("status", "pending"),
            "payment_method": data.get("payment_method", "credit_card"),
            "transaction_id": data.get("transaction_id"),
            "created_at": datetime.datetime.utcnow(),
            "updated_at": datetime.datetime.utcnow()
        }
        
        # Add car purchase details if present
        if "car_details" in data:
            payment_data["car_details"] = {
                "car_id": data["car_details"]["_id"],
                "brand": data["car_details"]["brand"],
                "model": data["car_details"]["model"],
                "year": data["car_details"]["year"],
                "price_per_day": data["car_details"]["price_per_day"],
                "transmission": data["car_details"]["transmission"],
                "fuel_type": data["car_details"]["fuel_type"],
                "engine": data["car_details"]["engine"],
                "mileage": data["car_details"]["mileage"],
                "seats": data["car_details"]["seats"],
                "doors": data["car_details"]["doors"]
            }
            
        return mongo.db.payments.insert_one(payment_data)

    @classmethod
    def get_payment_by_id(cls, payment_id):
        return cls.find_by_id(payment_id)

    @classmethod
    def get_payments_by_user(cls, user_id):
        return cls.find_all({"user_id": user_id})

    @classmethod
    def get_payments_by_rental(cls, rental_id):
        return cls.find_all({"rental_id": rental_id})

    @classmethod
    def update_payment_status(cls, payment_id, status):
        return cls.update(payment_id, {
            "status": status,
            "updated_at": datetime.datetime.utcnow()
        })

    @staticmethod
    def get_all():
        return list(mongo.db.payments.find())

    @staticmethod
    def get_by_id(payment_id):
        return mongo.db.payments.find_one({"_id": payment_id})

    @staticmethod
    def update(payment_id, data):
        update_data = {k: v for k, v in data.items() if v is not None}
        return mongo.db.payments.update_one(
            {"_id": payment_id},
            {"$set": update_data}
        )

    @staticmethod
    def delete(payment_id):
        return mongo.db.payments.delete_one({"_id": payment_id}) 