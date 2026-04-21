from __future__ import annotations

from datetime import datetime, timedelta

import click
from flask import Flask

from extensions import db
from models import Ticket


def register_commands(app: Flask) -> None:
    @app.cli.command("init-db")
    def init_db():
        """创建表并插入示例票务数据（幂等）。"""
        with app.app_context():
            db.create_all()

            has_any = db.session.query(Ticket.id).limit(1).first() is not None
            if not has_any:
                now = datetime.now()
                demo = [
                    Ticket(
                        title="示例演出：春季音乐会",
                        venue="城市音乐厅",
                        start_time=now + timedelta(days=3),
                        price_cents=19900,
                        stock=120,
                    ),
                    Ticket(
                        title="示例电影：科幻之夜",
                        venue="万达影城 3 号厅",
                        start_time=now + timedelta(days=1, hours=5),
                        price_cents=6900,
                        stock=80,
                    ),
                    Ticket(
                        title="示例话剧：人间喜剧",
                        venue="大剧院",
                        start_time=now + timedelta(days=10, hours=2),
                        price_cents=29900,
                        stock=60,
                    ),
                ]
                db.session.add_all(demo)
                db.session.commit()
                click.echo("已写入示例票务数据。")
            else:
                click.echo("已存在票务数据，跳过写入。")

    @app.cli.command("seed-tickets")
    @click.option("--count", default=10, show_default=True, type=int, help="追加多少条票务数据")
    def seed_tickets(count: int):
        """追加示例票务数据（可重复执行）。"""
        if count <= 0:
            click.echo("count 必须为正整数。")
            return

        with app.app_context():
            db.create_all()

            now = datetime.now()
            base = [
                ("电影：星际远航", "万达影城 IMAX 厅", 1, 4, 8900, 120),
                ("演唱会：夏日热浪", "体育中心", 7, 1, 39900, 500),
                ("话剧：茶馆", "人民艺术剧院", 3, 2, 15900, 180),
                ("脱口秀：周末专场", "城市剧场", 2, 0, 12900, 140),
                ("展览：未来科技展", "会展中心", 5, 6, 5000, 1000),
                ("音乐会：交响之夜", "城市音乐厅", 9, 3, 26900, 200),
                ("舞蹈：天鹅湖", "大剧院", 12, 2, 29900, 160),
                ("电影：悬疑之谜", "中影国际影城 5 号厅", 0, 6, 5900, 90),
                ("赛事：篮球联赛", "体育馆", 15, 1, 19900, 800),
                ("亲子：儿童剧《魔法森林》", "青少年宫剧场", 4, 1, 9900, 220),
            ]

            tickets: list[Ticket] = []
            for i in range(count):
                title, venue, d, h, price, stock = base[i % len(base)]
                tickets.append(
                    Ticket(
                        title=f"示例{title}（加数据#{i+1}）",
                        venue=venue,
                        start_time=now + timedelta(days=d, hours=h, minutes=(i * 7) % 60),
                        price_cents=price,
                        stock=stock,
                    )
                )

            db.session.add_all(tickets)
            db.session.commit()
            click.echo(f"已追加 {count} 条票务数据。")

