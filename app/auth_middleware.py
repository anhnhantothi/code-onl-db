# # app/auth_middleware.py
# from functools import wraps
# from flask import request, jsonify
# import jwt
# from .config import Config

# def token_required(f):
#     @wraps(f)
#     def decorated(*args, **kwargs):
#         token = None

#         # get token from header Authorization: Bearer <token>
#         if 'Authorization' in request.headers:
#             auth_header = request.headers['Authorization']
#             if auth_header.startswith('Bearer '):
#                 token = auth_header.split(' ')[1]

#         if not token:
#             return jsonify({'error': 'Token is missing'}), 401

#         try:
#             decoded = jwt.decode(token, Config.SECRET_KEY, algorithms=["HS256"])
#             # Giả sử bạn lưu user_id trong payload
#             request.user_id = decoded.get('user_id')
#         except jwt.ExpiredSignatureError:
#             return jsonify({'error': 'Token expired'}), 401
#         except jwt.InvalidTokenError:
#             return jsonify({'error': 'Invalid token'}), 401

#         return f(*args, **kwargs)
#     return decorated
