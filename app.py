import uuid

import certifi
from flask import Flask, render_template, abort, url_for, redirect, request, session
from pymongo import MongoClient
import stripe
from email_confirmation import send_confirmation_email
import os
from Database.mongo import product_collection
from Database.database_handler import insert_order
from notify_owner import notify_owner
from Database.database_handler import orders
app = Flask(__name__)
#MongoSet up
uri = os.environ['MONGO_URI']
client = MongoClient(uri, tlsCAFile=certifi.where())
db = client["Products"]
products = db["product"]

#Stripe setup
#stripe.api_key = os.environ['STRIPE_API_KEY']
app.secret_key = os.environ['APP_SECRET_KEY']
# ====================== ROUTES ========================
@app.route('/')
def hello_world():
    return render_template('index.html')

@app.route('/product/<slug>')
def product_detail(slug):
    product = products.find_one({"slug": slug})
    if not product:
        abort(404)
    return render_template("product.html", product=product)


@app.route('/add-to-cart/<slug>', methods=['POST'])
def add_to_cart(slug):
    product = products.find_one({"slug": slug})
    if not product:
        return "Product not found", 404

    size = request.form.get('size')
    color = request.form.get('color')

    cart = session.get('cart', [])
    cart.append({
        "name": product["name"],
        "price": product["price"],
        "slug": product["slug"],
        "size": size,
        "color": color,
    })

    session['cart'] = cart
    return redirect(url_for('cart'))

@app.route('/cart')
def cart():
    cart = session.get('cart', [])
    total = sum(item['price'] for item in cart)
    return render_template("cart.html", cart=cart, total=total)


@app.route('/remove-from-cart/<slug>')
def remove_from_cart(slug):
    cart = session.get('cart', [])
    cart = [item for item in cart if item['slug'] != slug]
    session['cart'] = cart
    return redirect(url_for('cart'))


# ================== CHECKOUT ====================
@app.route('/checkout')
def checkout():
    cart = session.get('cart', [])
    total = sum(item['price'] for item in cart)
    return render_template("checkout.html", cart=cart, total=total)

@app.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
    print("🔑 Stripe API key:", stripe.api_key)
    # Store shipping details in session
    session['shipping'] = {
        "first_name": request.form['first_name'],
        "last_name": request.form['last_name'],
        "email": request.form['email'],
        "phone": request.form['phone'],
        "address": request.form['address'],
        "address2": request.form.get('address2', ""),
        "city": request.form['city'],
        "state": request.form['state'],
        "zip": request.form['zip'],
    }

    cart = session.get('cart', [])
    if not cart:
        return redirect('/cart')

    subtotal = sum(item['price'] for item in cart)
    tax = round(subtotal * 0.07, 2)
    delivery_fee = 0
    total = subtotal + tax + delivery_fee

    # Build Stripe line items
    line_items = []
    for item in cart:
        line_items.append({
            'price_data': {
                'currency': 'usd',
                'product_data': {'name': item['name']},
                'unit_amount': int(item['price'] * 100),
            },
            'quantity': 1,
        })

    # Delivery fee
    line_items.append({
        'price_data': {
            'currency': 'usd',
            'product_data': {'name': 'Delivery Fee'},
            'unit_amount': int(delivery_fee * 100),
        },
        'quantity': 1,
    })

    # Sales Tax
    line_items.append({
        'price_data': {
            'currency': 'usd',
            'product_data': {'name': 'Sales Tax (7%)'},
            'unit_amount': int(tax * 100),
        },
        'quantity': 1,
    })

    # ✅ Create Stripe Checkout Session first
    checkout_session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=line_items,
        mode='payment',
        success_url=url_for('success', _external=True),
        cancel_url=url_for('cart', _external=True),
        customer_email=session['shipping']['email'],
    )

    # ✅ Now insert order with real session ID
    order_id = str(uuid.uuid4())
    shipping = session['shipping']
    order_details = [{
        "name": i["name"],
        "price": i["price"],
        "size": i.get("size"),
        "color": i.get("color"),
        "slug": i["slug"]
    } for i in cart]

    customer_order = {
        'order_id': order_id,
        'stripe_session_id': checkout_session.id,  # ✅ store actual ID
        'details': order_details,
        'name': shipping['first_name'],
        'email': shipping['email'],
        'phone': shipping['phone'],
        'address': shipping['address'],
        'city': shipping['city'],
        'state': shipping['state'],
        'zip': shipping['zip'],
        'status': 'pending'
    }

    insert_order(customer_order)

    # Redirect to Stripe checkout
    return redirect(checkout_session.url)

@app.route('/success')
def success():
    session.pop('cart', None)
    return "<h1>Order Successful!</h1><p>Your receipt has been emailed.</p>"

# ================== STRIPE WEBHOOK ====================
@app.route("/webhook", methods=["POST"])
def stripe_webhook():
    payload = request.data
    sig_header = request.headers.get("Stripe-Signature")

    try:
        event = stripe.Webhook.construct_event(payload, sig_header,)
    except Exception as e:
        return {"error": str(e)}, 400

    if event["type"] == "checkout.session.completed":
        data = event["data"]["object"]
        print(data)
        session_id = data["id"]

        # Get line items from Stripe
        line_items = stripe.checkout.Session.list_line_items(session_id)

        # Find the matching order in your MongoDB (FIX)
        order = orders.find_one({"stripe_session_id": session_id})
        if not order:
            print(f"No order found for session {session_id}")
            return {"status": "no_order"}, 200

        # Pull customer email safely
        email = data.get("customer_details", {}).get("email", order.get("email"))

        # Build a simplified shipping dict from your stored order
        shipping = {
            "first_name": order.get("name"),
            "email": order.get("email"),
            "address": order.get("address"),
            "city": order.get("city"),
            "state": order.get("state"),
            "zip": order.get("zip"),
        }

        send_confirmation_email(email, line_items, shipping)

        # ✅ Notify owner
        notify_owner(order)

        # Optionally mark order as completed
        orders.update_one(
            {"stripe_session_id": session_id},
            {"$set": {"status": "completed"}}
        )

    return {"status": "success"}, 200





if __name__ == '__main__':
    app.run(debug=True)