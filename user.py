from flask import (
    Blueprint, render_template, flash, redirect, url_for, request, g, jsonify, session
)
from werkzeug.exceptions import abort
from werkzeug.utils import secure_filename
import os
from datetime import date
from OnlineFoodOrderingSystem.auth import login_required, get_db
from OnlineFoodOrderingSystem.email import update_to_seller
from werkzeug.security import check_password_hash, generate_password_hash

us = Blueprint('user', __name__)

@us.route("/cart")
@login_required
def cart():
    try:
        with get_db() as db:
            id = g.user['id']
            data = db.execute('SELECT * FROM cart WHERE user_id=?', (id,)).fetchall()
            return render_template("user/cart.html", data=data, cart=data)
    except Exception as e:
        return f"Error fetching data: {e}", "error"
    
@us.route("/checkout")
@login_required
def checkout():
    try:
        with get_db() as db:
            id = g.user['id']
            cart = db.execute('SELECT * FROM cart WHERE user_id=?', (id,)).fetchall()
            return render_template("user/checkout.html", cart=cart)
    except Exception as e:
        return f"Error fetching data: {e}", "error"

@us.route("/proceed_to_checkout", methods=['POST'])
@login_required
def proceed_to_checkout():
    try:
        with get_db() as db:
            id = g.user['id']
            delivery = request.form.get('delivery')
            subtotal = request.form.get('subtotal')
            total = request.form.get('total')

            print(delivery)
            print(total)
            if delivery is None or total is None:
                cart = db.execute('SELECT * FROM cart WHERE user_id=?', (id,)).fetchall()
                return render_template("user/checkout.html", cart=cart)
            else:
                cart = db.execute('SELECT * FROM cart WHERE user_id=?', (id,)).fetchall()
                restaurant_id = set()
                for item in cart:
                    restaurant_id.add(item['res_id'])

                print(restaurant_id)

                return render_template("user/checkout.html", cart=cart, delivery=delivery, total=total, restaurant_id=restaurant_id, subtotal=subtotal)
    except Exception as e:
        return f"Error fetching data: {e}", "error"

@us.route("/dashboard")
@login_required
def dashboard():
    try:
        with get_db() as db:
            id = g.user['id']
            data = db.execute('SELECT * FROM reservations WHERE user_id=?', (id,)).fetchall()
            cart = db.execute('SELECT * FROM cart WHERE user_id=?', (id,)).fetchall()
            restaurant_query = 'SELECT * FROM restaurant'
            restaurant = db.execute(restaurant_query).fetchall()
            return render_template("user/dashboard.html", data=data, cart=cart, restaurant=restaurant)
    except Exception as e:
        return f"Error fetching data: {e}", "error"

@us.route("/dashboard-Manager")
@login_required
def dashboardManager():
    try:
        with get_db() as db:
            restaurant = g.user['restaurant_name']
            id = g.user['id']
            cat = db.execute('SELECT * FROM reservations WHERE restaurant=?', (restaurant,)).fetchall()
            category = db.execute('SELECT category FROM food_categories')
            
            data = db.execute('SELECT * FROM dishes WHERE res_id=?', (id,)).fetchall()
            restaurant_query = 'SELECT * FROM restaurant'
            restaurant = db.execute(restaurant_query).fetchall()
            return render_template("user/dashboardManager.html", cat=cat, category=category, data=data, restaurant=restaurant)
    except Exception as e:
        flash(f"Error fetching data: {e}", "error")
        return redirect(url_for("index"))
    
@us.route("/dashboard-Admin")
@login_required
def dashboardAdmin():
    try:
        with get_db() as db:
            res = db.execute('SELECT * FROM reservations').fetchall()
            data = db.execute('SELECT * FROM dishes').fetchall()
            today = str(date.today())
            category = db.execute('SELECT * FROM food_categories').fetchall()
            restaurant_query = 'SELECT * FROM restaurant'
            restaurant = db.execute(restaurant_query).fetchall()
            return render_template("user/dashboardAdmin.html", data=data, res = res, today=today, category=category, restaurant=restaurant)
    except Exception as e:
        return f"Error fetching data: {e}", "error"

@us.route('/create_reservation', methods=['POST'])
def create_reservation():
    db = get_db()  # Get a connection to the database.
    
    id = g.user['id']# Get the user name from the form data.
    restaurant = request.form['restaurant']
    fullname = request.form['full-name']
    number = request.form['number']
    date = request.form['date']
    time = request.form['time']
    party_size = request.form['party_size']
    
    # Check if the user with the given name exists in the database.
    user = db.execute("SELECT * FROM user WHERE id=?", (id,)).fetchone()
    if user is None:
        abort(404)  # If the user does not exist, return a 404 error.
    
    # Insert the reservation into the 'reservations' table.
    db.execute("""INSERT INTO reservations (
        user_id, restaurant, full_name,
        number, date, time, party_size
        ) VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (user['id'], restaurant, fullname, number, date, time, party_size))
    
    db.commit()  # Commit the transaction.
    db.close()  # Close the database connection.
    
    flash('Reservation created successfully.')
    return redirect(request.referrer)

@us.route('/add_dish', methods=['POST'])
def add_dish():    
    db = get_db()
    res_id = g.user['id']
    # Retrieve the values submitted in the form
    dish_name = request.form['dish_name']
    cuisine_type = request.form['cuisine_type']
    description = request.form['description']
    price = request.form['price']
    image = request.files.get('image')
    dietary_preference = request.form['dietary_preference']

    # Insert the values into the 'dishes' table
    db.execute("""INSERT INTO dishes (
        res_id, dish_name,
        cuisine_type, description,
        price, image, dietary_preference
        ) VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (res_id, dish_name, cuisine_type, description, price, image.filename, dietary_preference))
    
    print(image.filename)

    # Save the uploaded image to a static directory
    buffer_size = 10 * 1024 * 1024  # 10 MB in bytes
    image.save('OnlineFoodOrderingSystem/static/images/data-images/' + image.filename, buffer_size=buffer_size)


    # Commit the transaction and close the connection
    db.commit()
    db.close()

    # Redirect the user to the reservations index page.
    return redirect(url_for("user.dashboardManager"))

ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif', 'mp4', 'avi', 'mov'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_to_database(image_filename, video_filename, description, add_info, terms):
    db = get_db()
    res_id = g.user['id']
    db.execute('INSERT INTO media (res_id, image, video, description, add_info, terms) VALUES (?, ?, ?, ?, ?, ?)',
                (res_id, image_filename, video_filename, description, add_info, terms))
    db.commit()
    db.close()

@us.route('/upload', methods=['POST'])
def resData():
    if request.method == 'POST':
        # Get the image and video files from the form
        image = request.files.get('image')
        video = request.files.get('video')
        desc = request.form['description']
        add_info = request.form['add-info']
        terms = request.form['terms']

        # Check if the files are allowed
        if image and allowed_file(image.filename) and video and allowed_file(video.filename):
            # Save the files to the uploads folder
            buffer_size = 20 * 1024 * 1024  # 10 MB in bytes
            image_filename = secure_filename(image.filename)
            image.save('OnlineFoodOrderingSystem/static/images/data-restaurants/' + image_filename, buffer_size=buffer_size)
            video_filename = secure_filename(video.filename)
            video.save('OnlineFoodOrderingSystem/static/images/data-restaurants/' + video_filename, buffer_size=buffer_size)

            # Save the file information to the database
            save_to_database(image_filename, video_filename, desc, add_info, terms)

            return redirect(url_for("user.dashboardManager"))
        else:
            return 'Only images and videos are allowed'

@us.route("/add_to_cart/<int:id>")
@login_required
def addCart(id):
    try:
        with get_db() as db:
            user_id = g.user['id']
            
            details = db.execute('SELECT * FROM dishes WHERE id = ?', (id,)).fetchone()
        
            res_id = details['res_id']
            image = details['image']
            title = details['dish_name']
            price = details['price']
            total = details['price']
            
            db.execute('INSERT INTO cart (user_id, res_id, image, title, price, total) VALUES (?, ?, ?, ?, ?, ?)',
                (user_id, res_id, image, title, price, total))
            db.commit()
                    
            flash(f'{title} has been added to your cart!')
            return redirect(request.referrer)
    except Exception as e:
        return f"Error fetching data: {e}", "error"
    
@us.route("/cart/delete/<int:id>, <string:title>")
def deleteCart(id, title):
    try:
        with get_db() as db:            
            db.execute('DELETE FROM cart WHERE id = ?', [id])
            db.commit()
    
            flash(f'{title} removed from cart')
            # Return a success response
            return redirect(request.referrer)
    except Exception as e:
        return f"Error fetching data: {e}", "error"
    
@us.route("/dish/delete/<int:id>")
def deleteDish(id, title):
    try:
        with get_db() as db:            
            db.execute('DELETE FROM dishes WHERE id = ?', [id])
            db.commit()
    
            flash(f'{title} removed from cart')
            # Return a success response
            return redirect(request.referrer)
    except Exception as e:
        return f"Error fetching data: {e}", "error"
    
@us.route("/reservations/cancel/<int:id>")
def deleteRes(id):
    try:
        with get_db() as db:            
            db.execute('DELETE FROM reservations WHERE id = ?', [id])
            db.commit()
    
            flash(f'Reservation cancelled')
            # Return a success response
            return redirect(request.referrer)
    except Exception as e:
        return f"Error fetching data: {e}", "error"

@us.route("/cart/update", methods=['POST'])
def update_cart():
    try:
        with get_db() as db:
            id = g.user['id']
            data = db.execute('SELECT * FROM cart WHERE user_id=?', (id,)).fetchall()
            # Update the cart data based on the POST request
            if request.method == 'POST':
                # Extract all values from the form fields in the request
                item_ids = []
                for item in data:
                    item_id = item['id']
                    gg = item['res_id']
                    item_ids.append(gg)
                    quantity = int(request.form.get(f'quantity_{item_id}'))
                    total = float(request.form.get(f'total_{item_id}'))
                    db.execute('UPDATE cart SET quantity = ?, total = ? WHERE id = ?', (quantity, total, item_id,))
                    db.commit()

                print(item_ids)
                print(get_repeated_numbers(item_ids))
                


                # Return a success response
                flash(f'Cart updated')
                return redirect(url_for("user.cart"))
    except Exception as e:
        return f"Error fetching data: {e}", "error"
    
def get_repeated_numbers(lst):
    repeated_numbers = []
    for num in lst:
        if lst.count(num) > 1 and num not in repeated_numbers:
            repeated_numbers.append(num)
    return repeated_numbers


@us.route("/dish/rate/<int:id>", methods=['POST'])
def rate(id):
    try:
        with get_db() as db:
            data = db.execute('SELECT * FROM dishes WHERE id=?', (id,)).fetchone()
            if request.method == 'POST':
                dish_id = id
                rating = int(request.form['rating'])
                ratings = data['rating'] + rating
                reviews = data['reviews'] + 1
                
                db.execute('UPDATE dishes SET rating=?, reviews=? WHERE id=?', (ratings, reviews, dish_id))
                db.commit()
        
                # Return a success response
                flash(f'{rating} stars!, Thank you for your feedback')
                return redirect(request.referrer)
    except Exception as e:
        return f"Error fetching data: {e}", "error"
    
@us.route("/restaurant/rate/<int:id>", methods=['POST'])
def rateRes(id):
    try:
        with get_db() as db:
            data = db.execute('SELECT * FROM restaurant WHERE id=?', (id,)).fetchone()
            if request.method == 'POST':
                dish_id = id
                rating = int(request.form['rating'])
                ratings = data['rating'] + rating
                reviews = data['reviews'] + 1
                
                db.execute('UPDATE restaurant SET rating=?, reviews=? WHERE id=?', (ratings, reviews, dish_id))
                db.commit()
        
                # Return a success response
                flash(f'{rating} stars!, Thank you for your feedback')
                return redirect(request.referrer)
    except Exception as e:
        return f"Error fetching data: {e}", "error"
    
@us.route("/user-profile/update", methods=['POST'])
def update_user_profile():
    try:
        with get_db() as db:
            user_id = g.user['id']
            display_name = request.form.get('display_name')
            email = request.form.get('email')
            current_password = request.form.get('current_password')
            new_password = request.form.get('new_password')
            confirm_password = request.form.get('confirm_password')
            
            user_type = session.get('user_type')
            if user_type == 0:
            # Retrieve the user from the type1 database
                user = get_db().execute(
                    'SELECT * FROM user WHERE id = ?', (user_id,)
                ).fetchone()
            elif user_type == 1:
                # Retrieve the user from the type2 database
                user = get_db().execute(
                    'SELECT * FROM restaurant WHERE id = ?', (user_id,)
                ).fetchone()
                    # Check if the current password matches the one in the database
                if current_password and not check_password_hash(user['password'], current_password):
                    flash('Invalid password')
                    return f"Error updating profile: {e}", "error"
                
                # Check if the new passsword matches
                if new_password != confirm_password:
                    flash('Password mismatch')
                    return f"Error updating profile: {e}", "error"
                
                # Update the user record with the new data
                if display_name:
                    db.execute('UPDATE restaurant SET username=? WHERE id=?', (display_name, user_id))
                if email:
                    db.execute('UPDATE restaurant SET email=? WHERE id=?', (email, user_id))
                if new_password:
                    db.execute('UPDATE restaurant SET password=? WHERE id=?', (generate_password_hash(new_password), user_id))
            elif user_type == 2:
                # Retrieve the user from the type1 database
                user = get_db().execute(
                'SELECT * FROM user WHERE id = ?', (user_id,)
            ).fetchone()
            
            # Check if the current password matches the one in the database
            if current_password and not check_password_hash(user['password'], current_password):
                flash('Invalid password')
                return f"Error updating profile: {e}", "error"
            
            # Check if the new passsword matches
            if new_password != confirm_password:
                flash('Password mismatch')
                return f"Error updating profile: {e}", "error"
            
            # Update the user record with the new data
            if display_name:
                db.execute('UPDATE user SET username=? WHERE id=?', (display_name, user_id))
            if email:
                db.execute('UPDATE user SET email=? WHERE id=?', (email, user_id))
            if new_password:
                db.execute('UPDATE user SET password=? WHERE id=?', (generate_password_hash(new_password), user_id))
            db.commit()

            flash('Profile updated')
            return redirect(request.referrer)
    except Exception as e:
        return f"Error updating profile: {e}", "error"


    
'''@us.route("/cart/update/<int:id>")
def updateCart(id):
    try:
        with get_db() as db:            
            db.execute('UPDATE cart SET quantity =
            db.commit()
    
            # Return a success response
            return redirect(request.referrer)
    except Exception as e:
        return f"Error fetching data: {e}", "error"'''

@us.route("/wishlist")
@login_required
def wishlist():
    return render_template ("user/wishlist.html")

@us.route("/sell")
@update_to_seller
def sell():
    return render_template ("user/sell.html")

'''cart = ["milk", "tea", "fanta"]
i = 0
for item in cart:
  i += 1
print(i)
'''