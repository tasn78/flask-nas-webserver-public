import os
from dotenv import load_dotenv
import pymysql

pymysql.install_as_MySQLdb()

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-change-in-production'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'mysql+pymysql://nas_user:your_password@localhost/nas_db?charset=utf8mb4'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER') or '/path/to/nas/storage'
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024