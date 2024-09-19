import gridfs
from bson.objectid import ObjectId
from flask import send_file
from io import BytesIO
from gridfs.errors import NoFile
import mimetypes

class GridFSFileManager:
    def __init__(self, mongo_db, allowed_extensions):
        self.fs = gridfs.GridFS(mongo_db)
        self.allowed_extensions = allowed_extensions

    def allowed_file(self, filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in self.allowed_extensions

    def upload_file(self, file, user_id):
        if not self.allowed_file(file.filename):
            return {'error': f'File type not allowed. Allowed types: {", ".join(self.allowed_extensions)}'}, 400

        file_id = self.fs.put(file, filename=file.filename, metadata={'user_id': user_id})
        return {'message': 'File uploaded successfully', 'file_id': str(file_id)}, 201

    def get_file(self, file_id):
        try:
            file = self.fs.get(ObjectId(file_id))
            mime_type, _ = mimetypes.guess_type(file.filename)
            return send_file(BytesIO(file.read()), download_name=file.filename, mimetype=mime_type, as_attachment=True)
        except NoFile:
            return {'error': 'File not found'}, 404

    def delete_file(self, file_id):
        try:
            self.fs.delete(ObjectId(file_id))
            return {'message': 'File deleted successfully'}, 200
        except NoFile:
            return {'error': 'File not found'}, 404

    def get_user_files(self, user_id):
        files = self.fs.find({'metadata.user_id': user_id})
        file_list = [{'file_id': str(file._id), 'filename': file.filename} for file in files]
        if not file_list:
            return {'message': 'No files found for this user'}, 404
        return {'files': file_list}, 200


















# from mongoengine import *
# from flask import current_app, send_file
# from werkzeug.utils import secure_filename
# from bson.objectid import ObjectId
# from io import BytesIO
# import mimetypes
# import gridfs
# from datetime import datetime

# class GridFSFile(Document):
#     filename = StringField(required=True)
#     content_type = StringField()
#     length = IntField()
#     chunk_size = IntField(default=261120)
#     upload_date = DateTimeField(default=datetime.utcnow)
#     aliases = ListField(StringField())
#     metadata = DictField()
#     md5 = StringField()

#     allowed_extensions = {'pdf', 'txt', 'docx', 'mp3', 'wav', 'png', 'jpg', 'jpeg', 'mp4'}

#     meta = {'collection': 'fs.files'}

#     @classmethod
#     def allowed_file(cls, filename):
#         return '.' in filename and filename.rsplit('.', 1)[1].lower() in cls.allowed_extensions

#     @classmethod
#     def upload_file(cls, file, user_id):
#         if not cls.allowed_file(file.filename):
#             return {'error': f'File type not allowed. Allowed types: {", ".join(cls.allowed_extensions)}'}, 400

#         filename = secure_filename(file.filename)
#         content_type = file.content_type or mimetypes.guess_type(filename)[0]

#         fs = gridfs.GridFS(current_app.db)
#         file_id = fs.put(file, 
#                          filename=filename, 
#                          content_type=content_type, 
#                          metadata={'user_id': user_id})

#         grid_file = cls(
#             id=file_id,
#             filename=filename,
#             content_type=content_type,
#             length=file.content_length,
#             metadata={'user_id': user_id}
#         ).save()

#         return {'message': 'File uploaded successfully', 'file_id': str(file_id)}, 201

#     @classmethod
#     def get_file(cls, file_id):
#         try:
#             fs = gridfs.GridFS(current_app.db)
#             grid_file = fs.get(ObjectId(file_id))
#             return send_file(
#                 BytesIO(grid_file.read()),
#                 attachment_filename=grid_file.filename,
#                 mimetype=grid_file.content_type,
#                 as_attachment=True
#             )
#         except gridfs.errors.NoFile:
#             return {'error': 'File not found'}, 404

#     @classmethod
#     def delete_file(cls, file_id):
#         try:
#             fs = gridfs.GridFS(current_app.db)
#             fs.delete(ObjectId(file_id))
#             cls.objects(id=file_id).delete()
#             return {'message': 'File deleted successfully'}, 200
#         except gridfs.errors.NoFile:
#             return {'error': 'File not found'}, 404

#     @classmethod
#     def get_user_files(cls, user_id):
#         files = cls.objects(metadata__user_id=user_id)
#         if not files:
#             return {'message': 'No files found for this user'}, 404
#         file_list = [{'file_id': str(file.id), 'filename': file.filename} for file in files]
#         return {'files': file_list}, 200

#     def __repr__(self):
#         return f'<GridFSFile {self.filename}>'