import os
from app import app

class Config(object):
    DEBUG = False
    TESTING = False
    
    SECRET_KEY = os.urandom(24)
    
    ALLOWED_FILES_EXTENSIONS = ['PNG', 'GIF', 'PDF', 'JPG', 'JPEG']
    ALLOWED_FILES_AND_EXTENSIONS = {'IMAGE': ['PNG', 'GIF', 'JPG', 'JPEG'] , 'DOCUMENT': ['PDF']}
    # APP_ROOT = os.path.dirname(os.path.abspath(__file__))
    # UPLOAD_FOLDER = os.path.join(app.config['APP_ROOT'], 'static', 'uploads')
    SESSION_COOKIE_SECURE = True
    

class ProductionConfig(Config):
    DEBUG = False

class DevelopmentConfig(Config):
    DEBUG = True

class TestingConfig(Config):
    TESTING = True
