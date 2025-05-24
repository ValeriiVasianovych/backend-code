from app.extensions import mongo

class Rental:
    @staticmethod
    def get_all():
        return list(mongo.db.rentals.find({}, {"_id": 0}))

    @staticmethod
    def create(data):
        return mongo.db.rentals.insert_one(data)

    @staticmethod
    def find_by_id(rental_id):
        return mongo.db.rentals.find_one({"rental_id": rental_id}, {"_id": 0})

    @staticmethod
    def update(rental_id, data):
        return mongo.db.rentals.update_one({"rental_id": rental_id}, {"$set": data})

    @staticmethod
    def delete(rental_id):
        return mongo.db.rentals.delete_one({"rental_id": rental_id})
    
    @staticmethod
    def get_by_brand(car_brand):
        return list(mongo.db.rentals.find({"car_brand": car_brand}, {"_id": 0}))