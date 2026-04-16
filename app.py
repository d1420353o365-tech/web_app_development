"""
app.py
Flask 應用程式入口：初始化 app、設定 config、註冊 Blueprint。

執行方式：
    python app.py
或使用 Flask CLI：
    flask --app app.py run --debug
"""

import os
from flask import Flask, render_template

from app.models.database import init_app as db_init_app
from app.routes import auth_bp, recipe_bp, user_bp, admin_bp
from app.models.database import init_db

def create_app():
    """
    Application Factory：建立並設定 Flask app 實例。
    """
    app = Flask(__name__, instance_relative_config=True)
    
    # 基本設定
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY", "dev_secret_key"),
        DATABASE=os.path.join(app.instance_path, "database.db"),
    )

    # 確保 instance 資料夾存在
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # 初始化資料庫配置
    db_init_app(app)

    # 註冊 Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(recipe_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(admin_bp)

    # 註冊錯誤處理
    register_error_handlers(app)

    # 如果是開發環境且資料庫尚未建立，自動初始化 (可選)
    # 這裡我們不自動做，交由開發者指令執行
    
    return app


def register_error_handlers(app):
    """
    註冊全站錯誤頁面處理器。
    """
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(403)
    def forbidden(e):
        return render_template('errors/403.html'), 403


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
