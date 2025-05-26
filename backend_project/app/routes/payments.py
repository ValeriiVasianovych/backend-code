from flask import Blueprint, jsonify, request, render_template, url_for, redirect
from app.extensions import mongo
from app.utils.decorators import token_required
from bson import ObjectId
import stripe
from app.config import Config

payments_bp = Blueprint('payments', __name__)
stripe.api_key = Config.STRIPE_SECRET_KEY

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