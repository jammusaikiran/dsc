from flask_pymongo import PyMongo 
import logging
mongo=PyMongo()

def init_db(app):
        try:
            mongo.init_app(app)
            logging.info("MongoDB connected successfully.")
        except Exception as e:
            logging.error(f"Error connecting to MongoDB: {str(e)}")