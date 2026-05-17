from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from OnlineFoodOrderingSystem.auth import login_required
from OnlineFoodOrderingSystem.db import get_db

fo = Blueprint('food', __name__)

@fo.route("/")
def home():
    try:
        with get_db() as db:      
            query = '''
                SELECT r.*, m.*
                FROM restaurant r
                INNER JOIN media m ON r.id = m.res_id
            '''            
            restaurants = db.execute(query).fetchall()
            restaurant_query = 'SELECT * FROM restaurant'
            restaurant = db.execute(restaurant_query).fetchall()
            return render_template("food/index.html", restaurants=restaurants, restaurant=restaurant)
    except Exception as e:
        return f"Error fetching data: {e}", "error"

@fo.route("/index")
def index():
    try:
        with get_db() as db:      
            query = '''
                SELECT r.*, m.*
                FROM restaurant r
                INNER JOIN media m ON r.id = m.res_id
            '''
            restaurants = db.execute(query).fetchall()
            restaurant_query = 'SELECT * FROM restaurant'
            restaurant = db.execute(restaurant_query).fetchall()
            return render_template("food/index.html", restaurants=restaurants, restaurant=restaurant)
    except Exception as e:
        return f"Error fetching data: {e}", "error"

@fo.route("/view-menu/<int:id>", methods=['GET'])
def viewMenu(id):
    try:
        with get_db() as db:     
            menu = db.execute('SELECT * FROM dishes WHERE id = ?', (id,)).fetchone()
            print(menu)
            res_id = menu['res_id']
            restaurant = db.execute('SELECT * FROM restaurant WHERE id = ?', (res_id,)).fetchone()
            print(restaurant)

            dishes = db.execute('SELECT * FROM dishes WHERE res_id = ? AND id != ?', (menu['res_id'], id,)).fetchall()
            print(dishes)

            return render_template("food/view-menu.html", dishes=dishes, menu=menu, restaurant=restaurant)
    except Exception as e:
        return f"Error fetching data: {e}", "error"

@fo.route("/product/<int:id>")
def product(id):
    try:
        with get_db() as db:  
            detail = db.execute('SELECT * FROM media WHERE res_id = ?', (id,)).fetchone()
            
            restaurant = db.execute('SELECT * FROM restaurant WHERE id = ?', (id,)).fetchone()
                      
            dishes = db.execute('SELECT * FROM dishes WHERE res_id = ? AND id != ?', (detail['res_id'], id)).fetchall()
            return render_template("food/product.html", dishes=dishes, detail=detail, restaurant=restaurant)
    except Exception as e:
        return f"Error fetching data: {e}", "error"

@fo.route("/about")
def about():
    try:
        with get_db() as db:      
            restaurant_query = 'SELECT * FROM restaurant'
            restaurant = db.execute(restaurant_query).fetchall()
            return render_template("food/about.html", restaurant=restaurant)
    except Exception as e:
        return f"Error fetching data: {e}", "error"

@fo.route("/contact")
def contact():
    try:
        with get_db() as db:      
            restaurant_query = 'SELECT * FROM restaurant'
            restaurant = db.execute(restaurant_query).fetchall()
            return render_template("food/contact.html", restaurant=restaurant)
    except Exception as e:
        return f"Error fetching data: {e}", "error"

@fo.route("/category")
def category():
    try:
        with get_db() as db:
            data = db.execute('SELECT category FROM food_categories').fetchall()
            cat = db.execute('SELECT * FROM food_categories').fetchall()
            dishes = db.execute('SELECT * FROM dishes').fetchall()
            restaurant_query = 'SELECT * FROM restaurant'
            restaurant = db.execute(restaurant_query).fetchall()
            return render_template("food/category.html", data=data, cat=cat, dishes=dishes, restaurant=restaurant)
    except Exception as e:
        return f"Error fetching data: {e}", "error"


    
@fo.route("/category-2cols")
def category2():
    try:
        with get_db() as db:
            data = db.execute('SELECT category FROM food_categories')
            cat = db.execute('SELECT * FROM food_categories')
            
            dishes = db.execute('SELECT * FROM dishes')
            restaurant_query = 'SELECT * FROM restaurant'
            restaurant = db.execute(restaurant_query).fetchall()
            return render_template("food/category-2cols.html", data=data, cat=cat, dishes=dishes, restaurant=restaurant)
    except Exception as e:
        f"Error fetching data: {e}", "error"
    
@fo.route("/category-4cols")
def category4():
    try:
        with get_db() as db:
            data = db.execute('SELECT category FROM food_categories')
            cat = db.execute('SELECT * FROM food_categories')
            
            dishes = db.execute('SELECT * FROM dishes')
            restaurant_query = 'SELECT * FROM restaurant'
            restaurant = db.execute(restaurant_query).fetchall()
            return render_template("food/category-4cols.html", data=data, cat=cat, dishes=dishes, restaurant=restaurant)
    except Exception as e:
        f"Error fetching data: {e}", "error"
    
@fo.route("/category-list")
def category_list():
    try:
        with get_db() as db:
            data = db.execute('SELECT category FROM food_categories')
            cat = db.execute('SELECT * FROM food_categories')
            
            dishes = db.execute('SELECT * FROM dishes')
            restaurant_query = 'SELECT * FROM restaurant'
            restaurant = db.execute(restaurant_query).fetchall()
            return render_template("food/category-list.html", data=data, cat=cat, dishes=dishes, restaurant=restaurant)
    except Exception as e:
        f"Error fetching data: {e}", "error"

@fo.route("/privacy")
def privacy():
    try:
        with get_db() as db:
            restaurant_query = 'SELECT * FROM restaurant'
            restaurant = db.execute(restaurant_query).fetchall()
            return render_template("food/privacy.html", restaurant=restaurant)
    except Exception as e:
        f"Error fetching data: {e}", "error"

@fo.errorhandler(404)
def page_not_found(e):
    return render_template ("food/404.html"), 404