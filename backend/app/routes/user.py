from flask import Blueprint, jsonify, make_response, request
import bcrypt
import jwt
import os
import datetime
from app.database import mongo
from app.middleware.userMiddleware import token_required

user_bp = Blueprint('user', __name__)

def hash_password(password):
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def get_jwt_secret():
    secret = os.getenv('JWT_SECRET')
    if secret is None:
        raise RuntimeError("JWT_SECRET environment variable is not set.")
    return secret

@user_bp.route('/signup', methods=["POST"])
def signup():
    data = request.get_json()
    if mongo.db.users.find_one({"email": data['email']}):
        return jsonify({"message": "User exists with given email"}), 400
    if data['password'] != data['confirmPass']:
        return jsonify({"message": "Passwords don't match"}), 400
    
    try:
        data['password'] = hash_password(data['password'])
        data['created_at'] = datetime.datetime.utcnow()
        data['access_level'] = 'user'  # Default value
        data.pop('confirmPass')
        new_user = mongo.db.users.insert_one(data)

        payload = {
            "username": data['username'],
            "email": data['email'],
            'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=30)
        }

        token = jwt.encode(payload, key=get_jwt_secret(), algorithm='HS256')
        response = make_response(jsonify({'message': "User created successfully", "token": token, "username": data["username"]}))
        response.status_code = 201
        response.set_cookie('access_token', token, httponly=True, secure=True, samesite='None')
        return response
    except Exception as e:
        return jsonify({"message": f"Error creating user: {str(e)}"}), 500

@user_bp.route('/preferences', methods=["POST"])
@token_required
def set_preferences():
    token = request.cookies.get('access_token')
    if not token:
        return jsonify({"message": "User not found"}), 400
    decoded_user = jwt.decode(token, get_jwt_secret(), algorithms=['HS256'])

    data = request.get_json()
    preferences = {
        "industry": data.get("industry"),
        "language": data.get("language"),
        "llm_experience": data.get("llm_experience"),
        "rag_experience": data.get("rag_experience")
    }

    mongo.db.users.update_one(
        {"username": decoded_user['username']},
        {"$set": {"preferences": preferences}}
    )
    
    return jsonify({"message": "Preferences saved successfully"}), 200

@user_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = mongo.db.users.find_one({"username": data['username']})
    if not user:
        return jsonify({'message': "Username or email doesn't exist"}), 400
    if not bcrypt.checkpw(data['password'].encode('utf-8'), user['password'].encode('utf-8')):
        return jsonify({"message": "Incorrect password, please try again"}), 400

    payload = {
        "username": user['username'],
        "email": user['email'],
        'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=30)
    }
    
    token = jwt.encode(payload, get_jwt_secret(), algorithm='HS256')
    response = make_response(jsonify({'message': "User logged in successfully", "token": token, "username": data["username"]}))
    response.status_code = 200
    response.set_cookie('access_token', token, httponly=True, secure=True, samesite='None')
    
    return response

@user_bp.route('/logout', methods=['GET'])
def logout():
    response = make_response(jsonify({"message": "Logged out successfully"}))
    response.set_cookie('access_token', '', expires=0)
    return response

@user_bp.route('/find', methods=['GET'])
@token_required
def find():
    token = request.cookies.get('access_token')
    if not token:
        return jsonify({"message": "User not found"}), 400
    try:
        decoded_user = jwt.decode(token, get_jwt_secret(), algorithms=['HS256'])
        user = mongo.db.users.find_one({"username": decoded_user['username']})
        if user is None:
            return jsonify({"message": "User not found"}), 404
        return jsonify({"username": user['username'], 'email': user["email"], 'preferences': user.get("preferences", {})})
    except jwt.ExpiredSignatureError:
        return jsonify({"message": "Token has expired"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"message": "Invalid token"}), 401
