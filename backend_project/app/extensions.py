from flask_pymongo import PyMongo
from pymongo.server_api import ServerApi

mongo = PyMongo(server_api=ServerApi('1'))