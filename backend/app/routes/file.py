from flask import Flask, request, jsonify, send_file,Blueprint
from flask_pymongo import PyMongo
import gridfs
from bson.objectid import ObjectId
from io import BytesIO
import mimetypes
import jwt
from app.database import mongo
from app.middleware.userMiddleware import token_required
from app.models.fileModel import GridFSFileManager
from database import mongo
from dotenv import load_dotenv
import os
ALLOWED_EXTENSIONS = {'pdf', 'txt', 'docx'}

load_dotenv()
file_bp = Blueprint('user', __name__)
file_manager = GridFSFileManager(gridfs.GridFS(mongo.db), ALLOWED_EXTENSIONS) # type: ignore

# Helper function to decode JWT token and extract user ID
def get_user_id_from_token(token):
    try:
        decoded_token = jwt.decode(token, os.getenv.JWT_SECRET, algorithms=['HS256'])
        return decoded_token['user_id']
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

# Route for uploading a document
@file_bp.route('/upload_document', methods=['POST'])
@token_required
def upload_document():
    if 'file' not in request.files or 'token' not in request.cookies:
        return jsonify({'error': 'File or token not provided'}), 400

    file = request.files['file']
    token = request.cookies.get('token')
    user_id = get_user_id_from_token(token)

    if not user_id:
        return jsonify({'error': 'Invalid or expired token'}), 401

    response, status_code = file_manager.upload_file(file, user_id)
    return jsonify(response), status_code

# Route for retrieving a document by file_id
@file_bp.route('/get_document/<file_id>', methods=['GET'])
@token_required
def get_document(file_id):
    response = file_manager.get_file(file_id)
    if isinstance(response, tuple):
        return jsonify(response[0]), response[1]
    return response

# Route for deleting a document by file_id
@file_bp.route('/delete_document/<file_id>', methods=['DELETE'])
@token_required
def delete_document(file_id):
    response, status_code = file_manager.delete_file(file_id)
    return jsonify(response), status_code

# Route for getting all document names uploaded by the current user
@file_bp.route('/get_user_documents', methods=['GET'])
@token_required
def get_user_documents():
    token = request.cookies.get('access_token')
    user_id = get_user_id_from_token(token)

    if not user_id:
        return jsonify({'error': 'Invalid or expired token'}), 401

    response, status_code = file_manager.get_user_files(user_id)
    return jsonify(response), status_code

