from app.extensions import mongo
from bson import ObjectId
from datetime import datetime

class BaseModel:
    collection_name = None

    @classmethod
    def get_collection(cls):
        if not cls.collection_name:
            raise NotImplementedError("Collection name must be defined")
        return mongo.db[cls.collection_name]

    @classmethod
    def find_by_id(cls, id):
        if isinstance(id, str):
            id = ObjectId(id)
        return cls.get_collection().find_one({'_id': id})

    @classmethod
    def find_all(cls, query=None):
        if query is None:
            query = {}
        return list(cls.get_collection().find(query))

    @classmethod
    def create(cls, data):
        if 'created_at' not in data:
            data['created_at'] = datetime.utcnow()
        result = cls.get_collection().insert_one(data)
        data['_id'] = str(result.inserted_id)
        return data

    @classmethod
    def update(cls, id, data):
        if isinstance(id, str):
            id = ObjectId(id)
        data['updated_at'] = datetime.utcnow()
        result = cls.get_collection().update_one(
            {'_id': id},
            {'$set': data}
        )
        return result.modified_count > 0

    @classmethod
    def delete(cls, id):
        if isinstance(id, str):
            id = ObjectId(id)
        result = cls.get_collection().delete_one({'_id': id})
        return result.deleted_count > 0 