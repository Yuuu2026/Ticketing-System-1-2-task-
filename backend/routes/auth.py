from __future__ import annotations

from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token
from sqlalchemy import select

from extensions import db
from identity_utils import (
    is_valid_id_card,
    is_valid_phone,
    normalize_id_card,
    normalize_phone,
    user_public,
)
from models import User

bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@bp.post("/session")
def create_session():
    """
    用手机号 + 身份证号 + 姓名核验身份：
    - 新手机号：建档并签发 token
    - 已有手机号：身份证号必须一致，否则拒绝（防他人冒用该手机号查票）
    """
    data = request.get_json(silent=True) or {}
    phone = normalize_phone(data.get("phone") or "")
    id_card = normalize_id_card(data.get("id_card") or "")
    full_name = (data.get("full_name") or "").strip()

    if not is_valid_phone(phone):
        return jsonify({"message": "参数不合法：请输入 11 位中国大陆手机号"}), 400
    if not is_valid_id_card(id_card):
        return jsonify({"message": "参数不合法：身份证号应为 18 位（末位可为 X）或 15 位"}), 400
    if not full_name or len(full_name) > 64:
        return jsonify({"message": "参数不合法：姓名必填且不超过 64 字"}), 400

    user = db.session.execute(select(User).where(User.phone == phone)).scalar_one_or_none()
    if user:
        if user.id_card != id_card:
            return jsonify({"message": "核验失败：该手机号已绑定其他身份证号"}), 403
        user.full_name = full_name
        db.session.commit()
    else:
        user = User(phone=phone, id_card=id_card, full_name=full_name)
        db.session.add(user)
        db.session.commit()

    token = create_access_token(identity=str(user.id))
    return jsonify({"access_token": token, "user": user_public(user)})
