import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, current_app, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from OnlineFoodOrderingSystem.db import get_db
from datetime import datetime

#Creating an authentication blueprint
bp = Blueprint('auth', __name__)

@bp.route('/auth.register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['register-name']
        email = request.form['register-email']
        password = request.form['register-password']
        db = get_db()
        error = None

        if not username:
            error = 'Username is required.'
        elif not email:
            error = 'Email is required.'
        elif not password:
            error = 'Password is required.'

        if error is None:
            try:
                db.execute(
                    "INSERT INTO user (username, email, usertype, password) VALUES (?, ?, ?)",
                    (username, email, generate_password_hash(password)),
                )
                db.commit()
            except db.IntegrityError:
                error = f"User {username} or {email} is already registered."
            else:
                return redirect(url_for("auth.login"))

        flash(error)

    return render_template('auth/register.html')

@bp.route('/auth.registerBusiness', methods=('GET', 'POST'))
def registerBusiness():
    if request.method == 'POST':
        res_name = request.form['confirm-res']
        username = request.form['register-name']
        email = request.form['confirm-email']
        password = request.form['register-password']
        db = get_db()
        error = None

        if not username:
            error = 'Username is required.'
        elif not email:
            error = 'Email is required.'
        elif not password:
            error = 'Password is required.'
        elif not res_name:
            error = 'Restaurant name is required.'

        if error is None:
            try:
                db.execute(
                    "INSERT INTO restaurant (username, restaurant_name, email, password) VALUES (?, ?, ?, ?)",
                    (username, res_name, email, generate_password_hash(password)),
                )
                db.commit()
            except db.IntegrityError:
                error = f"User {username} or {email} is already registered."
            else:
                return redirect(url_for("auth.loginBusiness"))

        flash(error)

    return render_template('auth/registerBusiness.html')

    """_summary_ 
#Registers admin user
@bp.route('/auth.register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['register-name']
        usertype = 2
        email = request.form['register-email']
        password = request.form['register-password']
        db = get_db()
        error = None

        if not username:
            error = 'Username is required.'
        elif not email:
            error = 'Email is required.'
        elif not password:
            error = 'Password is required.'

        if error is None:
            try:
                db.execute(
                    "INSERT INTO user (username, email, usertype, password) VALUES (?, ?, ?, ?)",
                    (username, email, usertype, generate_password_hash(password)),
                )
                db.commit()
            except db.IntegrityError:
                error = f"User {username} or {email} is already registered."
            else:
                return redirect(url_for("auth.login"))

        flash(error)

    return render_template('auth/register.html')
    Returns:
        _type_: _description_
    """

#Creates your login form
@bp.route('/auth.login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        email = request.form['singin-email']
        password = request.form['singin-password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE email = ?', (email,)
        ).fetchone()

        if user is None:
            error = 'Incorrect Username or Email'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect Password.'
        elif user['isblocked'] == 1:
            error = "Your account is blocked, contact the administrator"

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            session['user_type'] = user['usertype']
            session['last_login'] = datetime.now()
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')

#Creates your login form
@bp.route('/auth.business', methods=('GET', 'POST'))
def loginBusiness():
    if request.method == 'POST':
        email = request.form['business-email']
        restaurant = request.form['business-restaurant']
        password = request.form['business-password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM restaurant WHERE email = ?', (email,)
        ).fetchone()

        if user is None:
            error = 'Incorrect Email'
        elif restaurant is None:
            error = 'Incorrect Restaurant Name'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect Password.'
        elif user['isblocked'] == 1:
            error = "Your account is blocked, contact the administrator"

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            session['user_type'] = user['usertype']
            session['last_login'] = datetime.now()
            return redirect(url_for('user.dashboardManager'))

        flash(error)

    return render_template('auth/loginBusiness.html')

#Create a before login validation request
@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        user_type = session.get('user_type')
        if user_type == 0:
            # Retrieve the user from the type1 database
            g.user = get_db().execute(
                'SELECT * FROM user WHERE id = ?', (user_id,)
            ).fetchone()
        elif user_type == 1:
            # Retrieve the user from the type2 database
            g.user = get_db().execute(
                'SELECT * FROM restaurant WHERE id = ?', (user_id,)
            ).fetchone()
        elif user_type == 2:
            # Retrieve the user from the type1 database
            g.user = get_db().execute(
                'SELECT * FROM user WHERE id = ?', (user_id,)
            ).fetchone()

    
#create a logout validation request   
@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('food.home'))

#Asks for login after logout
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view

@bp.route('/shutdown')
def shutdown():
    if not current_app.testing:
        return render_template ("fashion/404.html"), 404
    shutdown = request.environ.get('werkzeug.server.shutdown')
    if not shutdown:
        return render_template ("fashion/404.html"), 500
    shutdown()
    return 'Shutting down'