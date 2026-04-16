"""
app/routes/user.py
使用者 Blueprint — 處理一般使用者的個人功能頁面。

路由清單：
  GET  /user/favorites  — 顯示目前登入使用者的收藏食譜清單（需登入）
"""

from flask import Blueprint, render_template, redirect, url_for, session, flash

from app.models.favorite import Favorite
from app.routes.auth import login_required

user_bp = Blueprint("user", __name__, url_prefix="/user")


# ---------------------------------------------------------------------------
# 路由實作
# ---------------------------------------------------------------------------

@user_bp.route("/favorites", methods=["GET"])
@login_required
def favorites():
    """我的收藏清單頁面：顯示登入使用者所有已收藏的食譜。"""
    favorites = Favorite.get_by_user(session["user_id"])
    return render_template("user/favorites.html", favorites=favorites)
