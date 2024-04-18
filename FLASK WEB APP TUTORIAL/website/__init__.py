from flask import Flask

def create_app():
    app = Flask(__name__) # initialize Flask
    app.config['SECRET_KEY'] = 'keykeykey' # way to encrypt cookies, session data in our website, never share to public

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    return app
