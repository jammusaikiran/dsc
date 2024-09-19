import jwt 
from functools import wraps
from flask import jsonify,request,g
import os
from app.database import mongo

def token_required(f):
    @wraps(f)
    def decorated(*args,**kwargs):
        token=None
        if 'access_token' in request.cookies:
            token=request.cookies.get('access_token')
        if not token:
            return jsonify({"message":"Unauthorized access login to continue "}),401
        try:
            data=jwt.decode(token,os.getenv("JWT_SECRET"),algorithms='HS256')
            username=data['username']
            current_user= mongo.db.users.find_one({"username":username})
            if not current_user:
                return jsonify({'error': 'Invalid token'}), 401

            g.user = current_user

        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Login again'})

        return f(*args, **kwargs)
    return decorated
