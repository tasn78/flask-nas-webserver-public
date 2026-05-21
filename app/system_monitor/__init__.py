# app/system_monitor/__init__.py
from flask import Blueprint

bp = Blueprint('system_monitor', __name__)

from app.system_monitor import routes