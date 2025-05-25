from app import create_app
import os
import logging
from app.config import Config

app = create_app()

if __name__ == '__main__':
    # Настройка логов
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Log JWT secret key status
    if os.environ.get('JWT_SECRET_KEY'):
        logging.info("Using JWT secret key from environment variables")
    else:
        logging.info("Generated new JWT secret key")
        logging.debug(f"JWT Secret Key: {Config.JWT_SECRET_KEY}")
    
    # Отключаем небезопасные настройки в продакшене
    if os.environ.get('FLASK_ENV') != 'production':
        os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
        os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'
    
    app.run(host='0.0.0.0', port=8080, debug=os.environ.get('FLASK_ENV') != 'production')