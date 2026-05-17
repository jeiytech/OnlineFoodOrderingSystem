from flask import Flask, render_template
app = Flask(__name__)

'''@app.route('/')
def home():
    user_agent = request.headers.get('User-Agent')
    return f"<h1>Hi, {user_agent}</h1>"

@app.route('/greet')
def greet():
    return "<h1>Hi, how are you doing!</h1>"

@app.route('/cook')
def cook():
    response = make_response('<h1>Cookies</h1')
    response.set_cookie('answer', '42')
    return response

@app.route('/user/<name>')
def user(name):
    return f"<h1>Welcome, {name}</h1>"
'''

@app.route("/")
def index():
    return render_template ("fashion/index.html")

@app.route("/index")
def indexx():
    return render_template ("fashion/index.html")

@app.route("/login")
def logIn():
    return render_template ("auth/login.html")

@app.route("/register")
def Register():
    return render_template ("auth/register.html")

@app.route("/product")
def product():
    return render_template ("fashion/product.html")

@app.route("/about")
def about():
    return render_template ("fashion/about.html")

@app.route("/contact")
def contact():
    return render_template ("fashion/contact.html")

@app.route("/category")
def category():
    return render_template ("fashion/category.html")

@app.route("/cart")
def cart():
    return render_template ("fashion/cart.html")

@app.route("/checkout")
def checkout():
    return render_template ("user/checkout.html")

@app.route("/dashboard")
def dashboard():
    return render_template ("user/dashboard.html")

@app.route("/wishlist")
def wishlist():
    return render_template ("user/wishlist.html")

