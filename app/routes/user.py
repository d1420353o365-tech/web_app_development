"""
app/routes/user.py
使用者 Blueprint — 處理一般使用者的個人功能頁面。

路由清單：
  GET  /user/favorites  — 顯示目前登入使用者的收藏食譜清單（需登入）
"""

from flask import Blueprint, render_template, redirect, url_for, session, flash

from app.models.favorite import Favorite

user_bp = Blueprint("user", __name__, url_prefix="/user")


# ---------------------------------------------------------------------------
# 路由骨架
# ---------------------------------------------------------------------------

@user_bp.route("/favorites", methods=["GET"])
def favorites():
    """
    我的收藏清單頁面：顯示登入使用者所有已收藏的食譜。

    GET /user/favorites

    處理邏輯（待實作）：
    1. 確認 session 中有 user_id，否則 flash("請先登入") 並重導向登入頁
    2. Favorite.get_by_user(session["user_id"]) 取得收藏食譜列表
       （回傳包含食譜基本資訊的 dict list）
    3. 渲染模板，傳入 favorites list

    輸出：
    - 渲染模板 user/favorites.html
      context: favorites
    - 未登入 → redirect(url_for("auth.login_page"))
    """
    pass
