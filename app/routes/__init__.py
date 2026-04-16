"""
app/routes/__init__.py
匯入所有 Blueprint，供 app/__init__.py 統一註冊。
"""

from .auth import auth_bp
from .recipe import recipe_bp
from .user import user_bp
from .admin import admin_bp

__all__ = ["auth_bp", "recipe_bp", "user_bp", "admin_bp"]
