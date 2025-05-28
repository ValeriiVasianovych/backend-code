from flask import Blueprint, jsonify, request, render_template, url_for, redirect
from app.extensions import mongo
from app.utils.decorators import token_required
from bson import ObjectId
import stripe
from app.config import Config
from app.controllers.payment_controller import PaymentController

payments_bp = Blueprint('payments', __name__)
stripe.api_key = Config.STRIPE_SECRET_KEY
payment_controller = PaymentController()

@payments_bp.route('/create-checkout-session', methods=['POST'])
@token_required
def create_checkout_session(current_user):
    try:
        data = request.get_json()
        car_id = data.get('car_id')
        rental_days = data.get('rental_days', 1)

        if not car_id:
            return jsonify({'error': 'Car ID is required'}), 400

        car = mongo.db.cars.find_one({'_id': ObjectId(car_id)})
        if not car:
            return jsonify({'error': 'Car not found'}), 404

        total_price = car['price_per_day'] * rental_days

        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': f"{car['brand']} {car['model']} Rental",
                        'description': f"Rental for {rental_days} days",
                    },
                    'unit_amount': int(total_price * 100),  # Convert to cents
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=request.host_url + 'payments/success?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=request.host_url + 'payments/cancel',
            metadata={
                'car_id': str(car['_id']),
                'user_id': str(current_user['_id']),
                'rental_days': rental_days
            }
        )

        return jsonify({'id': checkout_session.id})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@payments_bp.route('/success')
def success():
    session_id = request.args.get('session_id')
    if session_id:
        try:
            session = stripe.checkout.Session.retrieve(session_id)
            return render_template('success.html', session=session)
        except Exception as e:
            return redirect(url_for('rentals.cars_page'))
    return redirect(url_for('rentals.cars_page'))

@payments_bp.route('/cancel')
def cancel():
    return render_template('cancel.html')

@payments_bp.route('/api/payments', methods=['POST'])
@token_required
def create_payment(current_user):
    return payment_controller.create_payment()

@payments_bp.route('/api/payments/<payment_id>', methods=['GET'])
@token_required
def get_payment(current_user, payment_id):
    return payment_controller.get_payment(payment_id)

@payments_bp.route('/api/payments/user/<user_id>', methods=['GET'])
@token_required
def get_user_payments(current_user, user_id):
    return payment_controller.get_user_payments(user_id)

@payments_bp.route('/api/payments/rental/<rental_id>', methods=['GET'])
@token_required
def get_rental_payments(current_user, rental_id):
    return payment_controller.get_rental_payments(rental_id)

@payments_bp.route('/api/payments/<payment_id>/status', methods=['PUT'])
@token_required
def update_payment_status(current_user, payment_id):
    return payment_controller.update_payment_status(payment_id)

@payments_bp.route('/payments', methods=['GET'])
@token_required
def get_payment_page(current_user):
    return payment_controller.get_payment_page() 