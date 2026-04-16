"""
app/models/database.py
資料庫連線管理與初始化工具。
提供 get_db() 取得連線，init_db() 初始化資料表。
"""

import sqlite3
import os
from flask import g, current_app


def get_db():
    """
    取得目前請求中的資料庫連線。
    若尚未建立連線，會自動建立並存入 Flask g 物件中（每次請求獨立）。
    """
    if "db" not in g:
        db_path = current_app.config.get(
            "DATABASE",
            os.path.join(current_app.instance_path, "database.db"),
        )
        g.db = sqlite3.connect(
            db_path,
            detect_types=sqlite3.PARSE_DECLTYPES,
        )
        g.db.row_factory = sqlite3.Row   # 讓查詢結果可以用欄位名稱存取
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(e=None):
    """
    關閉資料庫連線（由 Flask teardown_appcontext 自動呼叫）。
    """
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    """
    根據 database/schema.sql 初始化資料庫，建立所有資料表。
    通常只需在首次部署或重置時執行一次。
    """
    db = get_db()
    schema_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        "database",
        "schema.sql",
    )
    with open(schema_path, encoding="utf-8") as f:
        db.executescript(f.read())
    db.commit()


def init_app(app):
    """
    將資料庫工具註冊到 Flask app，由 app/__init__.py 呼叫。
    """
    app.teardown_appcontext(close_db)
