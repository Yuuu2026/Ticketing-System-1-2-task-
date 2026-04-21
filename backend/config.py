from __future__ import annotations

import os
from pathlib import Path


def _env(key: str, default: str | None = None) -> str | None:
    return os.getenv(key, default)


class Config:
    SECRET_KEY = _env("SECRET_KEY", "dev-secret")
    JWT_SECRET_KEY = _env("JWT_SECRET_KEY", "dev-jwt-secret")

    # 便捷模式：
    # - USE_SQLITE=1：无需 MySQL，直接用本地 sqlite 文件启动（适合“直接打开就能跑”）
    # - DB_URL：也可以直接指定 SQLAlchemy 的完整连接串
    USE_SQLITE = (_env("USE_SQLITE", "0") or "0") == "1"
    DB_URL = _env("DB_URL")

    DB_HOST = _env("DB_HOST", "127.0.0.1")
    DB_PORT = int(_env("DB_PORT", "3306") or 3306)
    DB_NAME = _env("DB_NAME", "ticketing")
    DB_USER = _env("DB_USER", "ticket")
    DB_PASSWORD = _env("DB_PASSWORD", "ticketpass")

    if DB_URL:
        SQLALCHEMY_DATABASE_URI = DB_URL
    elif USE_SQLITE:
        # 用绝对路径避免落到 Flask instance 目录，便于“直接打开运行”
        sqlite_path = (Path(__file__).resolve().parent / "ticketing.db").as_posix()
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{sqlite_path}"
    else:
        SQLALCHEMY_DATABASE_URI = (
            f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
            "?charset=utf8mb4"
        )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    FRONTEND_ORIGIN = _env("FRONTEND_ORIGIN", "http://127.0.0.1:5173")

