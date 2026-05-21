# app/file_manager/__init__.py
from flask import Blueprint

bp = Blueprint('file_manager', __name__)

from app.file_manager import routes