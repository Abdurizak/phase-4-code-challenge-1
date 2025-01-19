from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token,create_refresh_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Item
from datetime import timedelta

# Initialize Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['JWT_SECRET_KEY'] = 'your_jwt_secret_key'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)

# Initialize extensions
db.init_app(app)
jwt = JWTManager(app)

# Routes

## User Registration
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    hashed_password = generate_password_hash(data['password'])
    user = User(username=data['username'], email=data['email'], password=hashed_password)
    db.session.add(user)
    db.session.commit()
    return jsonify({"message": "User registered successfully!"}), 201

## User Login
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(username=data['username']).first()
    if not user or not check_password_hash(user.password, data['password']):
        return jsonify({"message": "Invalid credentials"}), 401
    access_token = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)
    return jsonify({"access_token": access_token, "refresh_token": refresh_token})


## Refresh Token
@app.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()
    new_access_token = create_access_token(identity=identity)
    return jsonify({"access_token": new_access_token})

## Fetch Current User
@app.route('/current_user', methods=['GET'])
@jwt_required()
def current_user():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    return jsonify({"username": user.username, "email": user.email})

## Create Item
@app.route('/items', methods=['POST'])
@jwt_required()
def create_item():
    data = request.json
    item = Item(name=data['name'], description=data['description'], price=data['price'])
    db.session.add(item)
    db.session.commit()
    return jsonify({"message": "Item created successfully!"}), 201

## Get All Items
@app.route('/items', methods=['GET'])
def get_items():
    items = Item.query.all()
    return jsonify([{
        "id": item.id, 
        "name": item.name, 
        "description": item.description, 
        "price": item.price
    } for item in items])

## Update or Delete Item
@app.route('/items/<int:item_id>', methods=['PUT', 'DELETE'])
@jwt_required()
def modify_item(item_id):
    item = Item.query.get_or_404(item_id)
    if request.method == 'PUT':
        data = request.json
        item.name = data.get('name', item.name)
        item.description = data.get('description', item.description)
        item.price = data.get('price', item.price)
        db.session.commit()
        return jsonify({"message": "Item updated successfully!"})
    elif request.method == 'DELETE':
        db.session.delete(item)
        db.session.commit()
        return jsonify({"message": "Item deleted successfully!"})

## Update User
@app.route('/user/update', methods=['PUT'])
@jwt_required()
def update_user():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    data = request.json
    user.username = data.get('username', user.username)
    user.email = data.get('email', user.email)
    db.session.commit()
    return jsonify({"message": "User details updated successfully!"})

## Update User Password
@app.route('/user/updatepassword', methods=['PUT'])
@jwt_required()
def update_password():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    data = request.json
    if not check_password_hash(user.password, data['old_password']):
        return jsonify({"message": "Old password is incorrect"}), 400
    user.password = generate_password_hash(data['new_password'])
    db.session.commit()
    return jsonify({"message": "Password updated successfully!"})

## Delete User Account
@app.route('/user/delete_account', methods=['DELETE'])
@jwt_required()
def delete_account():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "Account deleted successfully!"})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)