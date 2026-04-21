from __future__ import annotations



from flask import Blueprint, jsonify, request

from flask_jwt_extended import get_jwt_identity, jwt_required

from sqlalchemy import select

from sqlalchemy.exc import IntegrityError



from extensions import db

from identity_utils import is_valid_phone, normalize_phone

from models import Order, Ticket, User



bp = Blueprint("orders", __name__, url_prefix="/api/orders")





def _order_public(o: Order) -> dict:

    return {

        "id": o.id,

        "quantity": o.quantity,

        "total_cents": o.total_cents,

        "status": o.status,

        "created_at": o.created_at.isoformat(sep=" ", timespec="seconds"),

        "ticket": {

            "id": o.ticket.id,

            "title": o.ticket.title,

            "venue": o.ticket.venue,

            "start_time": o.ticket.start_time.isoformat(sep=" ", timespec="seconds"),

            "price_cents": o.ticket.price_cents,

        },

    }





@bp.post("")

@jwt_required()

def create_order():

    user_id = int(get_jwt_identity())

    data = request.get_json(silent=True) or {}

    ticket_id = data.get("ticket_id")

    quantity = data.get("quantity")



    if not isinstance(ticket_id, int) or not isinstance(quantity, int) or quantity <= 0:

        return jsonify({"message": "参数不合法：ticket_id/quantity 必填且为正整数"}), 400



    try:

        with db.session.begin():

            ticket = (

                db.session.execute(

                    select(Ticket).where(Ticket.id == ticket_id).with_for_update()

                )

                .scalars()

                .first()

            )

            if not ticket:

                return jsonify({"message": "票不存在"}), 404

            if ticket.stock < quantity:

                return jsonify({"message": "余票不足"}), 409



            ticket.stock -= quantity

            total_cents = ticket.price_cents * quantity

            order = Order(

                user_id=user_id,

                ticket_id=ticket.id,

                quantity=quantity,

                total_cents=total_cents,

                status="PAID",

            )

            db.session.add(order)



        return jsonify(_order_public(order)), 201

    except IntegrityError:

        db.session.rollback()

        return jsonify({"message": "下单失败（数据库约束错误）"}), 400





@bp.get("/<int:order_id>")

@jwt_required()

def get_order(order_id: int):

    user_id = int(get_jwt_identity())

    order = db.session.execute(select(Order).where(Order.id == order_id)).scalar_one_or_none()

    if not order:

        return jsonify({"message": "订单不存在"}), 404

    if order.user_id != user_id:

        return jsonify({"message": "无权限访问该订单"}), 403



    return jsonify(_order_public(order))





@bp.post("/lookup")

def lookup_orders_by_phone():

    """仅用手机号查询该号码关联用户的全部订单（含票务信息）。无需登录。"""

    data = request.get_json(silent=True) or {}

    phone = normalize_phone(data.get("phone") or "")

    if not is_valid_phone(phone):

        return jsonify({"message": "请输入有效的 11 位手机号"}), 400



    user = db.session.execute(select(User).where(User.phone == phone)).scalar_one_or_none()

    if not user:

        return jsonify([]), 200



    rows = (

        db.session.execute(select(Order).where(Order.user_id == user.id).order_by(Order.created_at.desc()))

        .scalars()

        .all()

    )

    return jsonify([_order_public(o) for o in rows]), 200





@bp.get("/me")

@jwt_required()

def my_orders():

    user_id = int(get_jwt_identity())

    rows = (

        db.session.execute(select(Order).where(Order.user_id == user_id).order_by(Order.created_at.desc()))

        .scalars()

        .all()

    )

    return jsonify([_order_public(o) for o in rows])


