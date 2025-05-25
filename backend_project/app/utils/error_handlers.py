from flask import jsonify

class ServiceError(Exception):
    def __init__(self, message, code=400):
        self.message = message
        self.code = code
        super().__init__(self.message)

def handle_error(error):
    if isinstance(error, ServiceError):
        response = {
            'error': error.message,
            'status': 'error'
        }
        return jsonify(response), error.code
    
    # Для неожиданных ошибок
    response = {
        'error': 'Internal server error',
        'status': 'error'
    }
    return jsonify(response), 500 