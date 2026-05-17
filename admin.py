from flask import (
    Blueprint,
    flash,
    g,
    redirect,
    render_template,
    request,
    url_for,
    session,
    json
)
from OnlineFoodOrderingSystem.auth import get_db
import string
from datetime import datetime
import socket
import re

ad = Blueprint("admin", __name__)

@ad.route("/blank")
def blank():
    return render_template ("admin/_blank.html")

@ad.route("/admin")
def admin():
    return render_template ("admin/index.html")

@ad.route("/customers")
def customers():
    try:
        with get_db() as db:
            usertype = 0
            data = db.execute('SELECT * FROM user WHERE usertype = ?', (usertype,)).fetchall()
            return render_template ("admin/customers.html", data=data)
    except Exception as e:
        return f"Error fetching data: {e}", "error"


@ad.route("/restaurants")
def restaurants():
    try:
        with get_db() as db:
            usertype = 1
            data = db.execute('SELECT * FROM restaurant WHERE usertype = ?', (usertype,)).fetchall()
            return render_template ("admin/restaurants.html", data=data)
    except Exception as e:
        return f"Error fetching data: {e}", "error"

@ad.route("/integration")
def integration():
    return render_template ("admin/integration.html")

@ad.route("/orders")
def orders():
    try:
        date = datetime.today().date()
        with get_db() as db:
            user_type = session.get('user_type')
            user_id = set([session.get('user_id')])
            
            id = session.get('user_id')
            
            orders = db.execute("SELECT * FROM orders").fetchall()
            
            item_lists = []
            for order in orders:
                res_id = str(user_id)
                purchased_items_str = order['purchased_items']
                purchased_items = purchased_items_str.replace('{', '').replace('}', '')
                print(purchased_items)
                print("")
                items = '{'+purchased_items+'}'
                items = items.replace("'", "\"")  # replace single quotes with double quotes
                items = json.loads(items)  # convert the string to a dictionary

                order_id = int(order['id'])
                print(order_id)

                # Get the values for each key
                titles = items['title'] if isinstance(items['title'], list) else [items['title']]
                quantities = items['quantity'] if isinstance(items['quantity'], list) else [items['quantity']]
                prices = items['price'] if isinstance(items['price'], list) else [items['price']]

                # Combine the values into a list of tuples
                item_list = zip(titles, quantities, prices) if isinstance(titles, list) else [(titles, quantities[0], prices[0])]
                item_list = [(order_id,) + item for item in item_list]  # add order_id to each tuple
                item_lists.append(item_list)
                print(item_lists)
                
                item_groups = {}

                for item_list in item_lists:
                    for item in item_list:
                        order_id = item[0]
                        if order_id in item_groups:
                            item_groups[order_id].append(item[1:])
                        else:
                            item_groups[order_id] = [item[1:]]

                print(item_groups)
                
            if user_type == 0:
                data = db.execute("SELECT * FROM orders WHERE date=? AND user_id = ?", (date, id,)).fetchall()
                modal = db.execute("SELECT * FROM orders WHERE date=? AND user_id = ?", (date, id)).fetchall()

            if user_type == 1:
                data = db.execute("SELECT * FROM orders WHERE date=? AND res_id = ?", (date, res_id,)).fetchall()
                modal = db.execute("SELECT * FROM orders WHERE date=? AND res_id = ?", (date, res_id)).fetchall()
                    
            elif user_type == 2:
                data = db.execute("SELECT * FROM orders WHERE date=?", (date,)).fetchall()
                modal = db.execute("SELECT * FROM orders WHERE date=?", (date,)).fetchall()

            return render_template ("admin/orders.html", data=data, modal=modal, item_lists=item_lists, order_id=order_id)
    except Exception as e:
        return f"Error fetching data: {e}", "error"



@ad.route("/products")
def products():
    try:
        with get_db() as db:
            data = db.execute('SELECT * FROM dishes').fetchall()
            return render_template ("admin/products.html", data=data)
    except Exception as e:
        return f"Error fetching data: {e}", "error"

@ad.route("/settings")
def settings():
    return render_template ("admin/settings.html")

@ad.route("/supports")
def supports():
    return render_template ("admin/supports.html")

@ad.route("/user-profile")
def userprofile():
    try:
        hostname = socket.gethostname()    
        ip_address = socket.gethostbyname(hostname)
        now = session.get('last_login')
        last_login = now.strftime("%d-%m-%Y  %H:%M:%S %p")
        with get_db() as db:
            if g.user['usertype'] == 2:
                data = db.execute('SELECT * FROM user WHERE usertype = 2').fetchone()
            elif g.user['usertype'] == 1:
                restaurant = g.user['restaurant_name']
                id = g.user['id']
                data = db.execute('SELECT * FROM restaurant WHERE restaurant_name=? and id= ?', (restaurant, id)).fetchone()
            return render_template ("admin/user-profile.html", data=data, ip_address=ip_address, hostname=hostname, last_login=last_login)
    except Exception as e:
        return f"Error fetching data: {e}", "error"
@ad.route("/mailbox")
def mailbox():
    try:
        with get_db() as db:
            if g.user['usertype'] == 2:
                id = g.user['usertype']
                messages = db.execute('SELECT * FROM contact_admin WHERE receipient_id=?', (id,)).fetchall()
            elif g.user['usertype'] == 1:
                id = g.user['id']
                messages = db.execute('SELECT * FROM contact_restaurant WHERE receipient_id=?', (id,)).fetchall()
            return render_template ("admin/mailbox.html", messages=messages)
    except Exception as e:
        return f"Error fetching data: {e}", "error"
    
@ad.route("/mail/delete/<int:id>")
def deleteMail(id):
    try:
        with get_db() as db:       
            if g.user['usertype'] == 2:     
                db.execute('DELETE FROM contact_admin WHERE id = ?', [id])
                db.commit()
            elif g.user['usertype'] == 1:
                receipient_id = g.user['id']
                db.execute('DELETE FROM contact_restaurant WHERE id = ? and receipient_id = ?', (id, receipient_id))

                db.commit()
            flash('Mail deleted!')
                # Return a success response
            return redirect(request.referrer)
    except Exception as e:
        return f"Error fetching data: {e}", "error"
    
@ad.route("/restaurant/block/<int:id>", methods=['GET', 'POST'])
def blockRestaurant(id):
    try:
        blocked = 1
        with get_db() as db:
            db.execute('UPDATE restaurant SET isblocked = ? WHERE id = ?', (blocked, id))
            db.commit()

            flash('Restaurant Blocked!')
            # Return a success response
            return redirect(request.referrer)
    except Exception as e:
        return f"Error fetching data: {e}", "error"


@ad.route("/restaurant/unblock/<int:id>", methods=['GET', 'POST'])
def unblockRestaurant(id):
    try:
        unblocked = 0
        with get_db() as db:
            db.execute('UPDATE restaurant SET isblocked = ? WHERE id = ?', (unblocked, id))
            db.commit()

            flash('Restaurant UnBlocked!')
            # Return a success response
            return redirect(request.referrer)
    except Exception as e:
        return f"Error fetching data: {e}", "error"
    
@ad.route("/user/block/<int:id>", methods=['GET', 'POST'])
def blockUser(id):
    try:
        blocked = 1
        with get_db() as db:
            db.execute('UPDATE user SET isblocked = ? WHERE id = ?', (blocked, id))
            db.commit()

            flash('Restaurant Blocked!')
            # Return a success response
            return redirect(request.referrer)
    except Exception as e:
        return f"Error fetching data: {e}", "error"


@ad.route("/user/unblock/<int:id>", methods=['GET', 'POST'])
def unblockUser(id):
    try:
        unblocked = 0
        with get_db() as db:
            db.execute('UPDATE user SET isblocked = ? WHERE id = ?', (unblocked, id))
            db.commit()

            flash('Restaurant UnBlocked!')
            # Return a success response
            return redirect(request.referrer)
    except Exception as e:
        return f"Error fetching data: {e}", "error"
    
@ad.route("/order/delivered/<int:id>,", methods=['GET', 'POST'])
def orderDelivered(id):
    try:
        delivered = 1
        with get_db() as db:
            db.execute('UPDATE orders SET delivery_status = ? WHERE id = ?', (delivered, id))
            db.commit()

            flash('Order Delivered!')
            # Return a success response
            return redirect(request.referrer)
    except Exception as e:
        return f"Error fetching data: {e}", "error"
    
@ad.route("/order/paid/<int:id>/<int:user_id>/<res_id>/<int:total>", methods=['GET', 'POST'])
def orderPaid(id, user_id, res_id, total):
    # Your code here
    try:
        paid = 1
        with get_db() as db:
            db.execute('UPDATE orders SET payment_status = ? WHERE id = ?', (paid, id))
            db.commit()
            
            user_data = db.execute('SELECT * FROM user WHERE id=?', (user_id,)).fetchone()
            purchased = user_data['purchased'] + total
            db.execute('UPDATE user SET purchased=? WHERE id=?', (purchased, user_id))
            db.commit()
            
            my_string = res_id  # A string with { and } characters
            my_string = my_string.replace("{", "").replace("}", "")  # Remove { and } characters
            rest_id = int(my_string) 
            res_data = db.execute('SELECT * FROM restaurant WHERE id=?', (rest_id,)).fetchone()
            purchased = res_data['sold'] + total
            db.execute('UPDATE restaurant SET sold=? WHERE id=?', (purchased, rest_id))
            db.commit()
            
            flash('Order Paid!')
            # Return a success response
            return redirect(request.referrer)
    except Exception as e:
        return f"Error fetching data: {e}", "error"
    
@ad.route("/delete/category/<int:id>")
def deleteCategory(id):
    try:
        with get_db() as db:       
            db.execute('DELETE FROM food_categories WHERE id = ?', [id])

            db.commit()
            flash('Category deleted!')
                # Return a success response
            return redirect(request.referrer)
    except Exception as e:
        return f"Error fetching data: {e}", "error"
    
@ad.route("/add/category", methods=['GET', 'POST'])
def addCategory():
    try:
        title = request.form.get('title')
        with get_db() as db:       
            category_exists = db.execute('SELECT 1 FROM food_categories WHERE category = ?', (title,)).fetchone() is not None
            if category_exists:
                flash('Category already exists!')
            else:
                db.execute('INSERT INTO food_categories (category) VALUES (?)', (title,))
                db.commit()
                flash('Category added!')

            # Return a success response
            return redirect(request.referrer)
    except Exception as e:
        return f"Error fetching data: {e}", "error"


@ad.route("/refresh")
def refresh():
    return redirect(request.referrer)


