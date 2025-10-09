from flask import Blueprint, request, jsonify
from models import db, Item, Order
from utils.auth import token_required
from datetime import datetime

order_bp = Blueprint('order_bp', __name__)

@order_bp.route('/order/create', methods=['POST'])
@token_required
def create_order(buyer_id):
    data = request.get_json()
    item_id = data.get('item_id')
    item = Item.query.get(item_id)

    if not item:
        return jsonify({'error': '商品不存在'}), 404
    if item.status != 0:
        return jsonify({'error': '商品不可购买'}), 400
    if item.user_id == buyer_id:
        return jsonify({'error': '不能购买自己发布的商品'}), 400

    # 创建订单
    order = Order(
        buyer_id=buyer_id,
        seller_id=item.user_id,
        item_id=item.id,
        price=item.price,
        status=0  # 待发货
    )

    # 修改商品状态为已售出
    item.status = 1
    db.session.add(order)
    db.session.commit()

    return jsonify({'msg': '下单成功', 'order_id': order.id})

@order_bp.route('/order/list', methods=['GET'])
@token_required
def get_orders(user_id):
    role = request.args.get('role', 'buyer')  # buyer / seller
    if role == 'seller':
        orders = Order.query.filter_by(seller_id=user_id).order_by(Order.create_time.desc()).all()
    else:
        orders = Order.query.filter_by(buyer_id=user_id).order_by(Order.create_time.desc()).all()

    result = []
    for o in orders:
        result.append({
            'id': o.id,
            'item_id': o.item_id,
            'price': o.price,
            'status': o.status,
            'create_time': o.create_time.isoformat(),
            'update_time': o.update_time.isoformat()
        })
    return jsonify(result)

@order_bp.route('/items/<int:item_id>/unlist', methods=['PUT'])
@token_required
def unlist_item(user_id, item_id):
    item = Item.query.get(item_id)
    if not item:
        return jsonify({'error': '商品不存在'}), 404
    if item.user_id != user_id:
        return jsonify({'error': '无权下架他人商品'}), 403

    item.status = 2  # 下架
    db.session.commit()
    return jsonify({'msg': '商品已下架'})

@order_bp.route('/order/<int:order_id>/ship', methods=['PUT'])
@token_required
def ship_order(user_id, order_id):
    order = Order.query.get(order_id)
    if not order:
        return jsonify({'error': '订单不存在'}), 404
    if order.seller_id != user_id:
        return jsonify({'error': '无权发货'}), 403
    if order.status != 0:
        return jsonify({'error': '订单状态错误，无法发货'}), 400

    order.status = 1  # 待收货
    order.update_time = datetime.utcnow()
    db.session.commit()
    return jsonify({'msg': '发货成功'})

@order_bp.route('/order/<int:order_id>/complete', methods=['PUT'])
@token_required
def complete_order(user_id, order_id):
    order = Order.query.get(order_id)
    if not order:
        return jsonify({'error': '订单不存在'}), 404
    if order.buyer_id != user_id:
        return jsonify({'error': '无权确认收货'}), 403
    if order.status != 1:
        return jsonify({'error': '订单状态错误，无法确认收货'}), 400

    order.status = 2  # 已完成
    order.update_time = datetime.utcnow()
    db.session.commit()
    return jsonify({'msg': '确认收货成功'})

@order_bp.route('/order/<int:order_id>/cancel', methods=['PUT'])
@token_required
def cancel_order(user_id, order_id):
    order = Order.query.get(order_id)
    if not order:
        return jsonify({'error': '订单不存在'}), 404
    if order.buyer_id != user_id:
        return jsonify({'error': '无权取消订单'}), 403
    if order.status not in (0, 1):
        return jsonify({'error': '订单状态错误，无法取消'}), 400

    order.status = 3  # 已取消
    order.update_time = datetime.utcnow()

    # 如果商品存在且为已售出，则重新上架
    item = Item.query.get(order.item_id)
    if item and item.status == 1:
        item.status = 0  # 重新上架

    db.session.commit()
    return jsonify({'msg': '订单已取消'})