from flask import Blueprint, request, jsonify

from model.request_response import RequestResponse
from models import db, Item
from utils.auth import token_required
import json

item_bp = Blueprint('item_bp', __name__)

@item_bp.route('/items', methods=['GET'])
def get_items():
    items = Item.query.filter_by(is_deleted=False).all()
    return jsonify(RequestResponse.success_response([{
        'id': i.id,
        'name': i.name,
        'price': i.price,
        'description': i.description,
        'image_urls': i.image_urls,
        'create_time': i.create_time.isoformat(),
        'people_want': i.people_want

    } for i in items]))

@item_bp.route('/items_my', methods=['GET'])
@token_required
def get_items_my(user_id):
    items = Item.query.filter_by(user_id=user_id, is_deleted=False).all()
    return jsonify(RequestResponse.success_response([{
        'id': i.id,
        'name': i.name,
        'price': i.price,
        'description': i.description,
        'image_urls': i.image_urls,
        'create_time': i.create_time.isoformat(),
        'people_want': i.people_want

    } for i in items]))




@item_bp.route('/items/upload', methods=['POST'])
@token_required
def upload_item(user_id):
    data = request.get_json()
    item = Item(
        user_id=user_id,
        name=data.get('name'),
        description=data.get('description'),
        price=data.get('price'),
        image_urls=data.get('image_url'),
        people_want=data.get('peole_want'),
    )
    db.session.add(item)
    db.session.commit()
    return jsonify(RequestResponse.success_response({
        'id': item.id,
        'name': item.name,
        'description': item.description,
        'price': item.price,
        'image_urls': item.image_urls,
        'create_time': item.create_time.isoformat(),
        'people_want': item.people_want
    }))

@item_bp.route('/items/<int:item_id>', methods=['PUT'])
@token_required
def update_item(user_id, item_id):
    item = Item.query.get(item_id)
    if not item:
        return jsonify(RequestResponse.error_response(code="999",msg="物品不存在"))
    if item.user_id != user_id:
        return jsonify(RequestResponse.error_response(code="999",msg="无权修改他人发布的物品"))


    data = request.get_json()
    item.name = data.get('name', item.name)
    item.description = data.get('description', item.description)
    item.price = data.get('price', item.price)
    item.image_urls = data.get('images', item.image_urls )

    db.session.commit()
    return jsonify(RequestResponse.success_response({}))

@item_bp.route('/items/<int:item_id>', methods=['DELETE'])
@token_required
def delete_item(user_id, item_id):
    item = Item.query.get(item_id)
    if not item:
        return jsonify(RequestResponse.error_response(code="999",msg="物品不存在"))

    if item.user_id != user_id:
        return jsonify(RequestResponse.error_response(code="999",msg="无权删除他人发布的物品"))

    item.is_deleted = True
    db.session.commit()
    return jsonify(RequestResponse.success_response({}))


@item_bp.route('/items/<int:item_id>', methods=['GET'])
def get_item_detail(item_id):
    item = Item.query.get(item_id)
    if not item or item.is_deleted:
        return jsonify(RequestResponse.error_response(code="999",msg="物品不存在"))

    return jsonify(RequestResponse.success_response({
        'id': item.id,
        'name': item.name,
        'description': item.description,
        'price': item.price,
        'image_urls': item.image_urls,
        'people_want': item.people_want
    }))


@item_bp.route('/items/search', methods=['GET'])
def search_items():
    keyword = request.args.get('keyword', '')
    page = int(request.args.get('page', 1))
    page_size = int(request.args.get('page_size', 10))

    query = Item.query.filter(Item.is_deleted == False)
    if keyword:
        query = query.filter(Item.name.like(f"%{keyword}%"))

    pagination = query.paginate(page=page, per_page=page_size, error_out=False)
    items = [{
        'id': i.id,
        'name': i.name,
        'price': i.price,
        'description': i.description,
        'image_urls': json.loads(i.image_urls or "[]"),
        'create_time': i.create_time.isoformat()
    } for i in pagination.items]


    return jsonify(RequestResponse.success_response({
        'total': pagination.total,
        'page': page,
        'page_size': page_size,
        'items': items
    }))

