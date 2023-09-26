from flask import request, jsonify, redirect,make_response
from app import app, db, SECRET_KEY
from models import User
from schemas import UserSchema
from flasgger.utils import swag_from
from logger import logger
from datetime import datetime, timedelta
from functools import wraps
import jwt


user_schema = UserSchema()
users_schema = UserSchema(many=True)


def decode_jwt(token):
    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return decoded
    except jwt.ExpiredSignatureError:
        return None;
    except jwt.InvalidTokenError:
        return None;
    
def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = get_token()
            
        if not token:
            return jsonify({"error": "Missing token"}), 401
        user_data = decode_jwt(token)
        if not user_data:
            return jsonify({"error": "Invalid or expired token"}), 401
        return f(*args, **kwargs)
    return decorated    
   
@app.before_request
def before_request_func():
    if request.method == 'OPTIONS':
        response = make_response()
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        response.headers.add('Access-Control-Allow-Headers', 'content-type')
        response.headers.add('Access-Control-Allow-Headers', 'authorization')
        return response

# ROUTE / 
# --------------------------------------------------------------------------
@app.route("/")
def index():
    return redirect("/apidocs")

# ROUTE /login - Special route do get JWT token
# --------------------------------------------------------------------------
@app.route("/login", methods=['POST'])
@swag_from('docs/login.yml')
def login():
    email = request.json.get('email')
    password = request.json.get('password')
    
    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({"error": "Invalid credentials"}), 401

    # Se as credenciais estiverem corretas, gere um token JWT
    expiration = datetime.utcnow() + timedelta(hours=1)  # token válido por 1 hora
    token = jwt.encode({'user_id': user.id, 'exp': expiration}, SECRET_KEY, algorithm='HS256')
    
    return jsonify({"token": token})


# ROUTE /users (POST) ADD A NEW USER
# --------------------------------------------------------------------------
@app.route("/users", methods=['POST'])
@swag_from('docs/add_user.yml')
@requires_auth
def add_user():
    name = request.json['name']
    email = request.json['email']
    password = request.json['password']
    new_user = User(name, email, password)
    
    try:
        db.session.add(new_user)
        db.session.commit()
        logger.info(f"New usser added:{name}")        
        return user_schema.jsonify(new_user)
    except Exception as e:
        logger.info(f"Error adding new user:{name}{e}")        
        db.session.rollback()
        return jsonify({"error": "Error addind user"}), 400
    
# ROUTE /users/nn (PUT) UPDATE THE USER
# --------------------------------------------------------------------------
@app.route("/user", methods=['PUT'])
@swag_from('docs/update_user.yml')
@requires_auth
def update_user(id):
    token = get_token()
    user_data = decode_jwt(token)
    user_id = user_data.get('user_id')  
        
    user = User.query.get(user_id)
    if user:    
        user.name = request.json['name']
        user.email = request.json['email']
        user.password = request.json['password']
        try:
            db.session.commit()
            logger.info(f"Updated user:{user.name}")        
            return user_schema.jsonify(user)
        except Exception as e:
            logger.info(f"Error updating user user:{user.name}: {e}")        
            db.session.rollback()
            return jsonify({"error": "Error updating user"}), 400



# ROUTE /users/<id> (GET) FIND USER BY ID (via Token)
# --------------------------------------------------------------------------
@app.route("/user", methods=['GET'])
@swag_from('docs/get_user.yml')
@requires_auth
def get_user():
    token = get_token()
    user_data = decode_jwt(token)
    user_id = user_data.get('user_id')    
    
    user = User.query.get(user_id)
    if user:
        logger.info(f"Getting user:{user.name}")        
        return user_schema.jsonify(user)
    else:
        logger.info(f"Error getting user:{user_id}:not found")        
        return jsonify({"error":"user not found"}), 404

# ROUTE /users/<id> (DELETE) DEL USER BY ID
# --------------------------------------------------------------------------
@app.route("/user", methods=['DELETE'])
@swag_from('docs/delete_user.yml')
@requires_auth
def delete_user():
    token = get_token()
    user_data = decode_jwt(token)
    user_id = user_data.get('user_id')    

    user = User.query.get(user_id)
    if user:
        db.session.delete(user)
        db.session.commit()
        logger.info(f"Deleting user:{user.name}")        
        return user_schema.jsonify(user)
    else:
        logger.info(f"Error getting user:{user_id}:not found")        
        return jsonify({"error":"user not found"}), 404
  

def get_token():
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith('Bearer '):
        token = auth_header.split('Bearer ')[1]
    else:
        token = None    
    return token