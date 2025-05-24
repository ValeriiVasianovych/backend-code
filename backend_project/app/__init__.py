from flask import Flask
import os
import pyfiglet
from app.extensions import mongo
import logging
from pymongo.server_api import ServerApi
from flask import request
import jwt
from app.config import Config
from bson import ObjectId

def create_app():
    app = Flask(__name__)
    
    # Load configuration before MongoDB initialization
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['MONGO_URI'] = f"mongodb+srv://{os.getenv('DB_USERNAME')}:{os.getenv('DB_PASSWORD')}@flaskdb.2ttjd.mongodb.net/car_rental?retryWrites=true&w=majority&appName=FlaskDB"
    
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    try:
        # MongoDB initialization
        mongo.init_app(app)
        logger.info("Successfully connected to MongoDB")
        logger.info("Connection Status: Active")
    except Exception as e:
        logger.error(f"MongoDB Connection Error: {str(e)}")
        raise e    

    ascii_banner = pyfiglet.figlet_format("Car Rentals API")
    print(ascii_banner)
    
    from app.routes.auth import auth_bp
    from app.routes.main import main_bp
    from app.routes.rentals import rentals_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(main_bp)
    app.register_blueprint(rentals_bp)

    @app.context_processor
    def inject_user():
        def get_current_user():
            token = None
            if 'Authorization' in request.headers:
                auth_header = request.headers['Authorization']
                try:
                    token = auth_header.split(" ")[1]
                    data = jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=['HS256'])
                    user_id = ObjectId(data['user_id'])
                    current_user = mongo.db.users.find_one({'_id': user_id})
                    if current_user:
                        current_user['is_authenticated'] = True
                        return current_user
                except:
                    pass
            return {'is_authenticated': False}
        return {'current_user': get_current_user()}

    return app