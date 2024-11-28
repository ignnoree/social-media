from flask import Flask
from cs50 import SQL
from flask_socketio import SocketIO

db = SQL('sqlite:///mydatabase.db')
socketio = SocketIO()

def create_app():
    app = Flask(__name__)
    app.secret_key = 'your_secret_key'
    app.config['DEBUG'] = True
    db.execute('PRAGMA foreign_keys = ON')

    from .routes import auth_routes, home_routes, profile_routes, direct_routes
    app.register_blueprint(auth_routes.bp)
    app.register_blueprint(home_routes.bp)
    app.register_blueprint(profile_routes.bp)
    app.register_blueprint(direct_routes.bp)

    socketio.init_app(app)
    return app
