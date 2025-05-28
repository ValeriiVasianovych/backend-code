from flask import request, render_template
from app.controllers.base_controller import BaseController
from app.models.payment import Payment
from app.utils.error_handlers import ServiceError
import logging

logger = logging.getLogger(__name__)

class PaymentController(BaseController):
    def create_payment(self):
        try:
            data = request.get_json()
            required_fields = ['user_id', 'amount']
            
            if not all(field in data for field in required_fields):
                return self.error_response("Missing required fields", 400)
            
            # Validate car details if present
            if "car_details" in data:
                required_car_fields = ['_id', 'brand', 'model', 'year', 'price_per_day']
                if not all(field in data["car_details"] for field in required_car_fields):
                    return self.error_response("Missing required car details", 400)
            
            payment = Payment.create_payment(data)
            return self.success_response(
                message="Payment created successfully",
                data={'payment_id': str(payment.inserted_id)}
            )
        except Exception as e:
            logger.error(f"Error creating payment: {str(e)}")
            return self.error_response("Internal server error", 500)

    def get_payment(self, payment_id):
        try:
            payment = Payment.get_payment_by_id(payment_id)
            if payment:
                payment['_id'] = str(payment['_id'])
                return self.success_response(data={'payment': payment})
            return self.error_response("Payment not found", 404)
        except Exception as e:
            logger.error(f"Error getting payment: {str(e)}")
            return self.error_response("Internal server error", 500)

    def get_user_payments(self, user_id):
        try:
            payments = Payment.get_payments_by_user(user_id)
            for payment in payments:
                payment['_id'] = str(payment['_id'])
            return self.success_response(data={'payments': payments})
        except Exception as e:
            logger.error(f"Error getting user payments: {str(e)}")
            return self.error_response("Internal server error", 500)

    def get_rental_payments(self, rental_id):
        try:
            payments = Payment.get_payments_by_rental(rental_id)
            for payment in payments:
                payment['_id'] = str(payment['_id'])
            return self.success_response(data={'payments': payments})
        except Exception as e:
            logger.error(f"Error getting rental payments: {str(e)}")
            return self.error_response("Internal server error", 500)

    def update_payment_status(self, payment_id):
        try:
            data = request.get_json()
            if 'status' not in data:
                return self.error_response("Status is required", 400)
            
            if Payment.update_payment_status(payment_id, data['status']):
                return self.success_response(message="Payment status updated successfully")
            return self.error_response("Payment not found", 404)
        except Exception as e:
            logger.error(f"Error updating payment status: {str(e)}")
            return self.error_response("Internal server error", 500)

    def get_payment_page(self):
        try:
            access_token = request.args.get('access_token')
            refresh_token = request.args.get('refresh_token')
            user_id = request.args.get('user_id')
            
            if not user_id:
                return render_template('error.html', message="User ID is required")
            
            payments = Payment.get_payments_by_user(user_id)
            for payment in payments:
                payment['_id'] = str(payment['_id'])
                
            return render_template('payments.html',
                payments=payments,
                access_token=access_token,
                refresh_token=refresh_token)
        except Exception as e:
            logger.error(f"Error getting payments page: {str(e)}")
            return render_template('error.html', message="Error loading payments") 