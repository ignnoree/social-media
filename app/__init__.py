from flask import Flask
from cs50 import SQL
from flask_socketio import SocketIO
from .utils import jwt
from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager
from flask_jwt_extended import set_access_cookies
from flask_jwt_extended import unset_jwt_cookies
from datetime import datetime
from datetime import timedelta
from datetime import timezone
from flask_wtf.csrf import CSRFProtect
from flask_caching import Cache

db = SQL('sqlite:///mydatabase.db')
socketio = SocketIO()
csrf = None 
cache = Cache()
def create_app():
    app = Flask(__name__)
    app.secret_key = 'd4160787ec22be41ffce4658942c0d94700acab31f8ed5af71ecbb911e7de63c'
    app.config['DEBUG'] = True
    csrf = CSRFProtect(app)
    db.execute('PRAGMA foreign_keys = ON')
    
    
    jwt = JWTManager(app)
    from .routes import auth_routes, home_routes, profile_routes, direct_routes,setting_routes
   
    app.register_blueprint(auth_routes.bp)
    app.register_blueprint(home_routes.bp)
    app.register_blueprint(profile_routes.bp)
    app.register_blueprint(direct_routes.bp)
    app.register_blueprint(setting_routes.bp)
    csrf.exempt(setting_routes.bp)
    csrf.exempt(auth_routes.bp)

   
    app.config["JWT_COOKIE_SECURE"] = False
    app.config['CACHE_TYPE']='simple'
    app.config["JWT_TOKEN_LOCATION"] = ["cookies"]
    app.config["JWT_SECRET_KEY"] = "e66eb10c72814805e0b443b56ef8a389cf91b4f26d12014be456cf1aba06b1e5"  # Change this to your secret key
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = 7 * 24 * 60 * 60 
    app.config['JWT_COOKIE_CSRF_PROTECT'] = False  

   
    jwt.init_app(app)
    socketio.init_app(app)
    cache.init_app(app)
    csrf.init_app(app)

    return app
