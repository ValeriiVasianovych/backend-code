from flask import jsonify
from app.utils.error_handlers import ServiceError

class BaseController:
    @staticmethod
    def success_response(data=None, message="Success", status_code=200):
        response = {
            'status': 'success',
            'message': message
        }
        if data is not None:
            response['data'] = data
        return jsonify(response), status_code

    @staticmethod
    def error_response(message="Error", status_code=400, error=None):
        response = {
            'status': 'error',
            'message': message
        }
        if error:
            response['error'] = str(error)
        return jsonify(response), status_code

    @staticmethod
    def handle_exception(e):
        if isinstance(e, ServiceError):
            return BaseController.error_response(
                message=e.message,
                status_code=e.status_code
            )
        return BaseController.error_response(
            message="Internal server error",
            status_code=500,
            error=str(e)
        ) 