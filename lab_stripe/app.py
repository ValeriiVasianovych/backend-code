import os
from flask import Flask, render_template, request, jsonify, redirect, url_for
import stripe
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
stripe_public_key = os.getenv('STRIPE_PUBLIC_KEY')

products = [
    {
        'id': 1,
        'name': 'MacBook 12" 2017',
        'price': 1299.99,
        'image': 'https://files.refurbed.com/ii/apple-macbook-2017-intel-core-12-1664789436.jpg?t=resize&h=630&w=1200'
    },
    {
        'id': 2,
        'name': 'MacBook Pro 16" 2021',
        'price': 8999.99,
        'image': 'https://tanimacbook.pl/wp-content/uploads/2024/08/apple-macbook-pro-a2442-m1-pro-max-120hz-miniled.jpg'
    },
    {
        'id': 3,
        'name': 'MacBook Air 13" 2024',
        'price': 4799.99,
        'image': 'https://m.media-amazon.com/images/I/81Fm0tRFdHL._AC_UF1000,1000_QL80_.jpg'
    }
]

@app.route('/')
def index():
    return render_template('index.html', products=products, stripe_public_key=stripe_public_key)

@app.route('/add_to_cart/<int:product_id>')
def add_to_cart(product_id):
    product = next((p for p in products if p['id'] == product_id), None)
    if product:
        return redirect(url_for('view_cart', product_id=product_id))
    return redirect(url_for('index'))

@app.route('/cart')
def view_cart():
    product_id = request.args.get('product_id')
    cart_items = []
    
    if product_id:
        product = next((p for p in products if p['id'] == int(product_id)), None)
        if product:
            cart_items.append(product)
    
    return render_template('cart.html', cart_items=cart_items, stripe_public_key=stripe_public_key)

@app.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
    try:
        product_id = int(request.form.get('product_id'))
        product = next((p for p in products if p['id'] == product_id), None)
        
        if not product:
            return jsonify({'error': 'Product not found'}), 404
        
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'pln',
                    'product_data': {
                        'name': product['name'],
                    },
                    'unit_amount': int(product['price'] * 100),  # Convert PLN to grosze
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=request.host_url + 'success?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=request.host_url + 'cancel',
        )
        return jsonify({'id': checkout_session.id})
    
    except Exception as e:
        print(f"Error creating checkout session: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/success')
def success():
    session_id = request.args.get('session_id')
    if session_id:
        session = stripe.checkout.Session.retrieve(session_id)
        return render_template('success.html', session=session)
    return redirect(url_for('index'))

@app.route('/cancel')
def cancel():
    return render_template('cancel.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
