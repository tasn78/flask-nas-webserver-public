# app/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from config import Config
from flask import Blueprint
import os


db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
login.login_view = 'auth.login'
bp = Blueprint('auth', __name__)


def ensure_directory_structure(app):
    upload_folder = app.config['UPLOAD_FOLDER']

    # Create shared folder
    shared_folder = os.path.join(upload_folder, 'shared')
    if not os.path.exists(shared_folder):
        os.makedirs(shared_folder)

    # Create users folder
    users_folder = os.path.join(upload_folder, 'users')
    if not os.path.exists(users_folder):
        os.makedirs(users_folder)

    # Create folders for existing users
    with app.app_context():
        from app.models import User
        users = User.query.all()
        for user in users:
            user_folder = os.path.join(users_folder, user.username)
            if not os.path.exists(user_folder):
                os.makedirs(user_folder)
                print(f"Created folder for user: {user.username}")


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)

    # Register blueprints
    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.file_manager import bp as file_bp
    app.register_blueprint(file_bp, url_prefix='/files')

    from app.user_manager import bp as user_bp
    app.register_blueprint(user_bp, url_prefix='/users')

    from app.system_monitor import bp as monitor_bp
    app.register_blueprint(monitor_bp, url_prefix='/monitor')

    from app.backup import bp as backup_bp
    app.register_blueprint(backup_bp, url_prefix='/backup')

    with app.app_context():
        ensure_directory_structure(app)

    return app