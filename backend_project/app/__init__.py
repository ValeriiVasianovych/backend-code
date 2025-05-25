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
from pymongo.errors import ConnectionFailure
from app.utils.error_handlers import handle_error
from app.utils.auth_utils import get_current_user
from app.routes.payments import payments_bp

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Load configuration before MongoDB initialization
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['MONGO_URI'] = f"mongodb+srv://{os.getenv('DB_USERNAME')}:{os.getenv('DB_PASSWORD')}@flaskdb.2ttjd.mongodb.net/car_rental?retryWrites=true&w=majority&appName=FlaskDB"
    
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    try:
        # MongoDB initialization
        mongo.init_app(app)
        
        # Test the connection with a ping
        mongo.db.command('ping')
        logger.info("Successfully connected to MongoDB")
        logger.info("Connection Status: Active")
        
        # Print ASCII banner only after successful connection
        ascii_banner = pyfiglet.figlet_format("Car Rentals API")
        print(ascii_banner)
        
    except ConnectionFailure as e:
        logger.error("Failed to connect to MongoDB")
        logger.error(f"Connection Error: {str(e)}")
        raise e
    except Exception as e:
        logger.error(f"MongoDB Connection Error: {str(e)}")
        raise e

    from app.routes.auth import auth_bp
    from app.routes.main import main_bp
    from app.routes.rentals import rentals_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(main_bp)
    app.register_blueprint(rentals_bp, url_prefix='/rentals')
    app.register_blueprint(payments_bp, url_prefix='/payments')

    # Register error handlers
    app.register_error_handler(Exception, handle_error)

    @app.context_processor
    def inject_user():
        return {'current_user': get_current_user()}

    @app.context_processor
    def inject_stripe_key():
        return dict(stripe_public_key=Config.STRIPE_PUBLIC_KEY)

    return app