from flask import Blueprint,jsonify, make_response,request
from app.database import mongo
import bcrypt,datetime,os
import jwt
user_bp=Blueprint('user',__name__)


def hash_password(password):
    salt=bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'),salt).decode('utf-8')
@user_bp.route('/signup',methods=["POST"])
def signup():
    data=request.get_json()
    if(mongo.db.users.find_one({"email":data['email']})):
        return jsonify({"message":"User exists with given email"}),400
    if data['password']!=data['confirmPass']:
        return jsonify({"message":"passwords don`t match"})
    try:
        data['password']=hash_password(data['password'])
        data['created_at'] = datetime.datetime.utcnow()
        data['access_level'] = 'user'  # or another default value
        data.pop('confirmPass')
        new_user=mongo.db.users.insert_one(data)
        payload={
            "username":data['username'],
            "email":data['email'],
            'exp':datetime.datetime.now(datetime.timezone.utc)+datetime.timedelta(days=30)
        }
        if new_user.inserted_id:
            token=jwt.encode(payload,key=os.getenv('JWT_SECRET'),algorithm='HS256')
            response=make_response(jsonify({'message':"user created sucessfully","token":token,"username":data["username"]}))
            response.status=201
            response.set_cookie('access_token', token,
                                httponly=True, secure=True, samesite='None')
            return response
        else:
            return jsonify({"message":"error in creating user "}),400
    except Exception as e:
        return jsonify({"message":f"error in creating user {str(e)}"}),500

@user_bp.route('/login',methods=['POST'])
def login():
    data=request.get_json()
    user=mongo.db.users.find_one({
            "username":data['username']})
    if not user:
         return jsonify({'message':"username or  email doesn`t exists"}),400
    if not bcrypt.checkpw(data['password'].encode('utf-8'), user['password'].encode('utf-8')):
        return jsonify({"message": "Incorrect password, please try again"}), 400
    payload={
        "username":user['username'],
        "email":user['email'],
        'exp':datetime.datetime.now(datetime.timezone.utc)+datetime.timedelta(days=30)
    }
    token=jwt.encode(payload,os.getenv('JWT_SECRET'),algorithm='HS256')

    response=make_response(jsonify({'message':"user created sucessfully","token":token,"username":data["username"]}))
    response.status=200
    response.set_cookie('access_token', token, 
                            httponly=True, secure=True, samesite='None')

    return response
@user_bp.route('/logout',methods=['GET'])
def logout():
    response=make_response(jsonify({"message":"Loged Out successfully"}))
    response.set_cookie('access_token',' ',expires=0)
    return response
@user_bp.route('/find',methods=['GET'])
def find():
    token=request.cookies.get('access_token')
    if not token:
        return jsonify({"message":"User not found"}),400
    decoded_user=jwt.decode(token,os.getenv('JWT_SECRET'),algorithms='HS256')
    user=mongo.db.users.find_one({"username":decoded_user['username']})  
    return jsonify({"username":user['username'],'email':user["email"]})  

    
