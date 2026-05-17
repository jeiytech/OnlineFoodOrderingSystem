from OnlineFoodOrderingSystem.db import get_db
from flask import Blueprint
du = Blueprint('dump', __name__)
import smtplib, ssl, os

@du.route("/dump_cat")
def dumpCat():
    db = get_db()
    categories =[('African',), ('Danish',), ('Italian',), ('Mexican',), ('Chinese',), ('Spanish',), ('Indian',), ('Japanese',), ('Greek',), ('Swedish',), ('Thai',), ('French',), ('English',)]
    db.executemany('Insert into food_categories (category) VALUES (?)', categories)
    db.commit()
    db.close()
    
    return "<h1>Dumped Categories/h1>"

@du.route("/alter")
def alterDish():
    db = get_db()
    db.execute('DELETE FROM orders')
    db.commit()

    return "Table has been Altered!"

@du.route("/delete_cat")
def deleteCat():
    db = get_db()
    db.execute("DELETE FROM sqlite_sequence WHERE name='orders';")
    db.commit()
    
    return "Table has been deleted!"

#Create foodtype database
@du.route("/create_foodtype")
def dumpFoodType():
    db = get_db()
    db.execute("""CREATE TABLE IF NOT EXISTS foodtype(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        food_type TEXT UNIQUE NOT NULL
        )
    """)
    db.commit()
    db.close()
    
    return "<h1>Created table foodtype</h1>"

#Create orders database
@du.route("/create_Order")
def dumpOrder():
    db = get_db()
    db.execute("""CREATE TABLE orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id TEXT UNIQUE NOT NULL,
        user_id INTEGER NOT NULL,
        res_id INTEGER NOT NULL,
        restaurant_name TEXT NOT NULL,
        date TEXT NOT NULL,
        delivery_fee INTEGER NOT NULL,
        delivery_status INTEGER NOT NULL DEFAULT 0,
        payment_status INTEGER NOT NULL DEFAULT 0,
        payment_method TEXT NOT NULL,
        purchased_items TEXT NOT NULL,
        quantity INTEGER NOT NULL,
        price INTEGER NOT NULL,
        total INTEGER NOT NULL,
        full_name TEXT NOT NULL,
        street_address TEXT NOT NULL,
        phone_number TEXT NOT NULL,
        order_notes TEXT,
        FOREIGN KEY (user_id) REFERENCES user(id),
        FOREIGN KEY (res_id) REFERENCES cart(res_id)
    );
    """)
    db.commit()
    db.close()
    
    return "<h1>Created table Orders</h1>"

#Creates the restaurant table
@du.route('/create_res')
def create_res():
    db = get_db()
    db.execute('''CREATE TABLE restaurant (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        restaurant_name TEXT UNIQUE NOT NULL,
        usertype TINYINT NOT NULL DEFAULT 1,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
        )
    ''')
    db.commit()
    db.close()
    
    return "<h1>Dumped Restaurants</h1>"

#Creates the reservation table
@du.route('/create_reserve')
def create_reseerve():
    db = get_db()
    db.execute('''CREATE TABLE reservations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        restaurant TEXT NOT NULL,
        full_name TEXT NOT NULL,
        number TEXT NOT NULL,
        date TEXT NOT NULL,
        time TEXT NOT NULL,
        party_size INTEGER NOT NULL,
        FOREIGN KEY (user_id) REFERENCES user(id)
        )
    ''')
    db.commit()
    db.close()
    
    return "<h1>Dumped Reservations</h1>"

# Creates the contact form table
@du.route('/create_contact_restaurant')
def create_contact_form():
    db = get_db()
    db.execute('''CREATE TABLE contact_restaurant (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        receipient_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        email TEXT NOT NULL,
        phone TEXT NOT NULL,
        subject TEXT NOT NULL,
        message TEXT NOT NULL,
        message_type TEXT NOT NULL,
        date TEXT NOT NULL,
        FOREIGN KEY (receipient_id) REFERENCES restaurant(id)
        );
    ''')
    db.commit()
    db.close()
    
    return "<h1>Created contact_form table</h1>"


#Creates the dishes table
@du.route('/create_dish')
def create_dish():
    db = get_db()
    db.execute('''CREATE TABLE dishes (
        id INTEGER PRIMARY KEY,
        res_id INTEGER NOT NULL,
        dish_name TEXT NOT NULL,
        cuisine_type TEXT NOT NULL,
        description TEXT NOT NULL,
        price REAL NOT NULL,
        image BLOB NOT NULL,
        dietary_preference TEXT NOT NULL,
        FOREIGN KEY (res_id) REFERENCES restaurant(id)
        )
    ''')
    db.commit()
    db.close()
    
    return "<h1>Dumped Dishes</h1>"

#Creates the dishes table
@du.route('/create_info')
def create_info():
    db = get_db()
    db.execute('''CREATE TABLE media
        (id INTEGER PRIMARY KEY AUTOINCREMENT,
        res_id INTEGER NOT NULL,
        image BLOB NOT NULL,
        video BLOB NOT NULL,
        description TEXT NOT NULL,
        add_info TEXT NOT NULL,
        terms TEXT NOT NULL,
        FOREIGN KEY (res_id) REFERENCES restaurant(id)
        );
    ''')
    db.commit()
    db.close()
    
    return "<h1>Dumped Info</h1>"

#Creates the dishes table
@du.route('/add_cart')
def addto():
    db = get_db()
    db.execute('''CREATE TABLE cart
        (id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        res_id INTEGER NOT NULL,
        image BLOB NOT NULL,
        title TEXT NOT NULL,
        quantity INTEGER NOT NULL DEFAULT 1,
        price INTEGER NOT NULL,
        total INTEGER NOT NULL,
        FOREIGN KEY (user_id) REFERENCES user(id),
        FOREIGN KEY (res_id) REFERENCES restaurant(id)
        );
    ''')
    db.commit()
    db.close()
    
    return "<h1>Dumped Cart</h1>"
    
@du.route('/sendSmtp')
def sendSmtp():
    
    port = 465 #for ssl
    smtp_server = "smtp.gmail.com"
    sender_email = 'thrift.stores.shop@gmail.com' #os.environ.get('MAIL_USERNAME')
    receiver_email = 'jeiytech3@gmail.com'
    password = 'Thrift.9090.<>[]' #os.environ.get('MAIL_PASSWORD')
    message = "This is an e-mail message to be sent in HTML format"
    
    print(sender_email)
    context = ssl.create_default_context()
    try:
        with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
            server.ehlo()
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message)
            print("Successfully sent email")
            return "<h1>Email Sent</h1>"
    except smtplib.SMTPAuthenticationError as e:
        print("Error: unable to authenticate with SMTP server:", e)
        return "<h1>Error: unable to send email AuthenticationError</h1>"
    except smtplib.SMTPConnectError as e:
        print("Error: unable to connect to SMTP server:", e)
        return "<h1>Error: unable to send email Connection Error</h1>"