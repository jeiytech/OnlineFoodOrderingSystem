from flask import (
    Blueprint,
    flash,
    g,
    redirect,
    render_template,
    current_app,
    request,
    url_for,
)
import re
from flask_mail import Message, Mail
import functools
import smtplib
import os
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import COMMASPACE, formatdate
from OnlineFoodOrderingSystem.auth import login_required, get_db
from werkzeug.security import check_password_hash, generate_password_hash


em = Blueprint("email", __name__)

#Update usertype on the table
def register_user(user_email):
    username = request.form['register-name']
    restaurant_name = request.form['confirm-res']
    password = request.form['register-password']
    db = get_db()
    error = None

    if not user_email:
            error = 'Email is required.'
    elif not restaurant_name:
            error = 'Password is required.'
    elif not password:
        error = 'Password is required.'

    if error is None:
        try:
            db.execute(
                "INSERT INTO restaurant (username, email, restaurant_name, password) VALUES (?, ?, ?, ?)",
                (username, user_email, restaurant_name, generate_password_hash(password)),
            )
            db.commit()
        except db.IntegrityError:
            error = f"User {user_email} or {restaurant_name} is already registered."
        else:
            return redirect(url_for("auth.business"))
        
    flash(error)
    
    return True

@em.route('/submit_contact_admin', methods=['POST'])
@login_required
def submit_contact_admin():
    if request.method == 'POST':
        try:
            with get_db() as db:  
                recipient_id = 2 # replace with the ID of the user who will receive the email
                full_name = request.form['cname']
                email = request.form['cemail']
                phone = request.form['cphone']
                subject = request.form['csubject']
                message = request.form['cmessage']
                message_type = request.form['cpoint']
                now = datetime.now()
                date = now.strftime("%d/%m/%Y %H:%M:%S")

                # Validate email and phone number
                email_pattern = r'^[\w-]+(\.[\w-]+)*@[a-zA-Z0-9-]+(\.[a-zA-Z0-9-]+)*(\.[a-zA-Z]{2,})$'
                if not re.match(email_pattern, email):
                    return "Invalid email address", "error"
                phone_pattern = r'^\+?[0-9]{7,}$'
                if not re.match(phone_pattern, phone):
                    return "Invalid phone number", "error"

                # Insert the values into the 'contact_admin' table
                db.execute("""INSERT INTO contact_admin (
                    receipient_id, name, email,
                    phone, subject, message, message_type, date
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                    (recipient_id, full_name, email, phone, subject, message, message_type, date))
                
                # Commit the transaction and close the connection
                db.commit()

                # Redirect the user to a thank you page or back to the contact form page
                flash('Message sent to Administrator')
                return redirect(url_for("food.contact"))
        except Exception as e:
            # Log the error and return a user-friendly error message
            current_app.logger.error(f"Error submitting contact form: {e}")
            return f"An error occurred while processing your request: {e}", "error"

@em.route('/submit_contact_restaurant', methods=['POST'])
@login_required
def submit_contact_restaurant():
    if request.method == 'POST':
        try:
            with get_db() as db:  
                recipient_id = request.form['receipient_id'] # replace with the ID of the user who will receive the email
                full_name = request.form['cname']
                email = request.form['cemail']
                phone = request.form['cphone']
                subject = request.form['csubject']
                message = request.form['cmessage']
                message_type = request.form['cpoint']
                now = datetime.now()
                date = now.strftime("%d/%m/%Y %H:%M:%S")

                # Validate email and phone number
                email_pattern = r'^[\w-]+(\.[\w-]+)*@[a-zA-Z0-9-]+(\.[a-zA-Z0-9-]+)*(\.[a-zA-Z]{2,})$'
                if not re.match(email_pattern, email):
                    return "Invalid email address", "error"
                phone_pattern = r'^\+?[0-9]{7,}$'
                if not re.match(phone_pattern, phone):
                    return "Invalid phone number", "error"

                # Insert the values into the 'contact_restaurant' table
                db.execute("""INSERT INTO contact_restaurant (
                    receipient_id, name, email,
                    phone, subject, message, message_type, date
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                    (recipient_id, full_name, email, phone, subject, message, message_type, date))
                
                # Commit the transaction and close the connection
                db.commit()

                # Redirect the user to a thank you page or back to the contact form page
                flash('Message sent to Restaurant')
                return redirect(request.referrer)
        except Exception as e:
            # Log the error and return a user-friendly error message
            current_app.logger.error(f"Error submitting contact form: {e}")
            return f"An error occurred while processing your request: {e}", "error"

'''@em.route("/auth.email")
def seller():
    return render_template ("user/sellerRequest.html")'''

def update_to_seller(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user['usertype'] == 0:
            return redirect(url_for('email.send_email_and_redirect'))
        elif g.user['usertype'] == 1:
            return redirect(url_for('/sell'))

        return view(**kwargs)

    return wrapped_view