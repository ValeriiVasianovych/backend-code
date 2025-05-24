# app/services/payment_service.py
from flask import jsonify
from app.models.rental import Rental
from app.models.user import User
from app.config import Config
import requests

class PaymentService:
    @staticmethod
    def process_google_pay_payment(rental_id, payment_token):
        # Mock Google Pay payment processing (replace with actual gateway integration)
        rental = Rental.find_by_id(rental_id)
        if not rental:
            return jsonify({"error": "Rental not found"}), 404

        # Simulate payment gateway request
        payment_data = {
            "gateway": Config.GOOGLE_PAY_GATEWAY,
            "gatewayMerchantId": Config.GOOGLE_PAY_GATEWAY_MERCHANT_ID,
            "amount": rental["rental_price"],
            "currency": "USD",
            "paymentMethodData": payment_token
        }

        # Replace with actual payment gateway API call
        try:
            # Example: response = requests.post("https://gateway.example.com/process", json=payment_data)
            response = {"status": "success", "transaction_id": "txn_123456"}  # Mock response
            if response["status"] == "success":
                Rental.update_payment_status(rental_id, "completed")
                User.add_payment_method(rental["username"], {
                    "type": "google_pay",
                    "transaction_id": response["transaction_id"],
                    "last_four": payment_token.get("last_four", "N/A"),
                    "created_at": str(datetime.datetime.utcnow())
                })
                return jsonify({"message": "Payment processed successfully", "transaction_id": response["transaction_id"]}), 200
            else:
                return jsonify({"error": "Payment failed"}), 400
        except Exception as e:
            return jsonify({"error": f"Payment error: {str(e)}"}), 500