"""
app.py
Flask 應用程式入口：初始化 app、設定 config、註冊 Blueprint。

執行方式：
    python app.py
或使用 Flask CLI：
    flask --app app run --debug
"""

import os
from flask import Flask, render_template

from app.models.database import init_app as db_init_app
from app.routes import auth_bp, recipe_bp, user_bp, admin_bp


def create_app():
    """
    Application Factory：建立並設定 Flask app 實例。

    處理邏輯（待實作）：
    1. 初始化 Flask app，指定 instance_path 為 ./instance
    2. 設定 SECRET_KEY（從環境變數或預設值）
    3. 設定 DATABASE 路徑（instance/database.db）
    4. 確保 instance/ 資料夾存在
    5. 呼叫 db_init_app(app) 掛載 DB 連線管理
    6. 呼叫 init_db() 初始化資料表（若尚未建立）
    7. 註冊所有 Blueprint
    8. 註冊 404 / 403 錯誤頁面處理器
    9. 回傳 app

    回傳：
    - Flask app 實例
    """
    pass


# ---------------------------------------------------------------------------
# 錯誤頁面處理（待實作）
# ---------------------------------------------------------------------------

def register_error_handlers(app):
    """
    註冊全站錯誤頁面處理器。

    處理邏輯（待實作）：
    - 404 → 渲染 errors/404.html
    - 403 → 渲染 errors/403.html
    """
    pass


# ---------------------------------------------------------------------------
# 程式進入點
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
