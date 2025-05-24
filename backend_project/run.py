from app import create_app
import os
import logging

app = create_app()

if __name__ == '__main__':
    # Настройка логов
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'
    app.run(host='0.0.0.0', port=8080, debug=True)