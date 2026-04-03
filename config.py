import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'REDACTED_SECRET_KEY'
    # Defaulting to localhost MySQL, no password, as this is a common dev setup
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'mysql+pymysql://root:REDACTED_DB_PASSWORD@localhost/bloodbridge'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
