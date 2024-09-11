import os

class Config:
    SECRET_KEY=os.getenv('SECRET_KEY')
    MONGO_URI=os.getenv('MONGO_URI')
    DEBUG=False
class DevelopmentConfig(Config):
     DEBUG=True
class ProductionConfig(Config):
     DEBUG=False
