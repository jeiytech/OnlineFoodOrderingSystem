from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort
from OnlineFoodOrderingSystem.db import get_db
from datetime import datetime
import random

ord = Blueprint('orders', __name__)

@ord.route("/add/order", methods=['POST'])
def make_order():
    try:
        with get_db() as db:
            user_id = g.user['id']
            data = db.execute('SELECT * FROM cart WHERE user_id=?', (user_id,)).fetchall()
            print(f"data: {data}")
            
            # Group the cart items by res_id
            grouped_items = {}
            for item in data:
                res_id = item['res_id']
                if res_id not in grouped_items:
                    grouped_items[res_id] = []
                grouped_items[res_id].append(item)

            # Insert each group of items as a separate order
            for res_id, items in grouped_items.items():
                item_ids = set()
                quantities = []
                prices = []
                titles = []

                fullname = request.form['fullname']
                address = request.form['address']
                phone = request.form['phone']
                notes = request.form['notes']
                delivery = float(request.form['delivery'])
                payment_method = request.form['payment_method']
                date = datetime.today().date()
                
                order_id = "ORD" + str(random.randint(100, 9999))

                total = 0.0

                for item in items:
                    item_id = item['id']
                    res_id = item['res_id']
                    qty = item['quantity']
                    pri = item['price']
                    tt = item['title']
                    
                    item_ids.add(res_id)

                    quantities.append(qty)
                    prices.append(pri)
                    titles.append(tt)

                    total += float(qty) * float(pri)

                total += delivery

                purchased_items = {
                    'id': item_ids,
                    'title': titles,
                    'quantity': quantities,
                    'price': prices,
                }
                
                res_name = db.execute('SELECT * FROM restaurant WHERE id=?', (res_id,)).fetchone()
                restaurant_name = res_name['restaurant_name']
                
                payment_status = 0 if payment_method == "ondelivery" else 1
                
                db.execute('''INSERT INTO orders (order_id, user_id, res_id, restaurant_name, date, delivery_fee, payment_method, payment_status, purchased_items, quantity, price, total, full_name, street_address, phone_number, order_notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                (order_id, user_id, str(item_ids), restaurant_name, date, delivery, payment_method, payment_status, str(purchased_items), str(quantities), str(prices), total, fullname, address, phone, notes))
                db.commit()
                
                if payment_status == 1:
                    user_data = db.execute('SELECT * FROM user WHERE id=?', (user_id,)).fetchone()
                    new_amount = user_data['purchased'] + total
                    db.execute('UPDATE user SET purchased=?, last_order=? WHERE id=?', (new_amount, date, user_id))
                    db.commit()

                    res_data = db.execute('SELECT * FROM restaurant WHERE id=?', (res_id,)).fetchone()
                    new_amount = res_data['sold'] + total
                    db.execute('UPDATE restaurant SET sold=?, last_order=? WHERE id=?', (new_amount, date, res_id))
                    db.commit()
                else:
                    db.execute('UPDATE user SET last_order=? WHERE id=?', (date, user_id))
                    db.commit()
                    
            db.execute('DELETE FROM cart WHERE user_id=?', (user_id,))
            db.commit()

            print(f"item_ids: {item_ids}")
            
            # Return a success response
            flash(f'Made Order')
            return redirect(url_for("user.cart"))
    except Exception as e:
        print(f"Error: {e}")
        return f"Error fetching data: {e}", "error"



