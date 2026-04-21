from __future__ import annotations

from flask import Blueprint, jsonify
from sqlalchemy import select

from extensions import db
from models import Ticket

bp = Blueprint("tickets", __name__, url_prefix="/api/tickets")


@bp.get("")
def list_tickets():
    rows = db.session.execute(select(Ticket).order_by(Ticket.start_time.asc())).scalars().all()
    return jsonify(
        [
            {
                "id": t.id,
                "title": t.title,
                "venue": t.venue,
                "start_time": t.start_time.isoformat(sep=" ", timespec="seconds"),
                "price_cents": t.price_cents,
                "stock": t.stock,
            }
            for t in rows
        ]
    )

