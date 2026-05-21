# app/user_manager/__init__.py
from flask import Blueprint

bp = Blueprint('user_manager', __name__)

from app.user_manager import routes