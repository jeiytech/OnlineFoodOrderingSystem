import os

from flask import Flask


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'foodOrder.sqlite'),
    )
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 465
    app.config['MAIL_USE_SSL'] = True
    app.config['MAIL_USERNAME'] = 'go.foodie.eat@gmail.com'


    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello, World!'
    
    from . import db
    db.init_app(app)
    
    from . import auth
    app.register_blueprint(auth.bp)
    
    from . import food
    app.register_blueprint(food.fo)
    app.add_url_rule('/', endpoint='index')
    
    from . import user
    app.register_blueprint(user.us)
    
    from . import orders
    app.register_blueprint(orders.ord)
    
    from . import email
    app.register_blueprint(email.em)
    
    from . import admin
    app.register_blueprint(admin.ad)
    
    from . import dumpDB
    app.register_blueprint(dumpDB.du)
    
    return app