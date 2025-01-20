from flask import Flask, request, jsonify,Blueprint
from models import db,  Item
from flask_jwt_extended import JWTManager, create_access_token,create_refresh_token, jwt_required, get_jwt_identity

Item_bp=Blueprint("Item_bp" ,__name__)

## Create Item
@Item_bp.route('/items', methods=['POST'])
@jwt_required()
def create_item():
    data = request.json
    item = Item(name=data['name'], description=data['description'], price=data['price'])
    db.session.add(item)
    db.session.commit()
    return jsonify({"message": "Item created successfully!"}), 201

## Get All Items
@Item_bp.route('/items', methods=['GET'])
def get_items():
    items = Item.query.all()
    return jsonify([{
        "id": item.id, 
        "name": item.name, 
        "description": item.description, 
        "price": item.price
    } for item in items])

## Update or Delete Item
@Item_bp.route('/items/<int:item_id>', methods=['PUT', 'DELETE'])
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