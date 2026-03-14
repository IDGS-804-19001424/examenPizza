import os
from sqlalchemy import create_engine

class Config(object):
    SECRET_KEY = "ClaveSecretaExamen"
    SECRET_COOKIE_SECURE = False

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:shifuMo29@127.0.0.1/examenPizza' 
    SQLALCHEMY_TRACK_MODIFICATIONS = False