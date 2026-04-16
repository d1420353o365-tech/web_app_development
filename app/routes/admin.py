"""
app/routes/admin.py
管理後台 Blueprint — 提供管理員專屬的使用者與食譜管理功能。
所有路由皆需要管理員權限（session["is_admin"] == True）。

路由清單：
  GET  /admin/                          — 後台總覽面板（統計數字）
  GET  /admin/users                     — 使用者列表
  POST /admin/users/<int:id>/delete     — 刪除指定使用者
  GET  /admin/recipes                   — 全站食譜列表（含私人）
  POST /admin/recipe/<int:id>/delete    — 強制刪除指定食譜
"""

from flask import Blueprint, render_template, redirect, url_for, session, flash, abort

from app.models.user import User
from app.models.recipe import Recipe

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


# ---------------------------------------------------------------------------
# 輔助：管理員權限檢查（在 implementation 階段實作）
# ---------------------------------------------------------------------------

def admin_required(f):
    """裝飾器：確認使用者具有管理員身份，否則 abort(403)。"""
    pass


# ---------------------------------------------------------------------------
# 路由骨架
# ---------------------------------------------------------------------------

@admin_bp.route("/", methods=["GET"])
def dashboard():
    """
    管理後台總覽面板。（需管理員）

    GET /admin/

    處理邏輯（待實作）：
    1. 確認 session["is_admin"] == True，否則 abort(403)
    2. User.get_all() 取得使用者列表，計算總數
    3. Recipe.get_all(public_only=False) 取得所有食譜，計算總數
    4. 取最新 5 筆食譜作為 recent_recipes

    輸出：
    - 渲染模板 admin/dashboard.html
      context: user_count, recipe_count, recent_recipes
    """
    pass


@admin_bp.route("/users", methods=["GET"])
def list_users():
    """
    使用者管理列表頁面。（需管理員）

    GET /admin/users

    處理邏輯（待實作）：
    1. 確認管理員身份，否則 abort(403)
    2. User.get_all() 取得所有使用者（依建立時間降序）

    輸出：
    - 渲染模板 admin/users.html
      context: users
    """
    pass


@admin_bp.route("/users/<int:id>/delete", methods=["POST"])
def delete_user(id):
    """
    強制刪除使用者帳號（CASCADE 刪除其所有食譜與收藏）。（需管理員）

    POST /admin/users/<int:id>/delete
    URL 參數: id — 使用者 id

    處理邏輯（待實作）：
    1. 確認管理員身份，否則 abort(403)
    2. User.get_by_id(id)，若不存在 → abort(404)
    3. 防止管理員刪除自己的帳號
    4. User.delete(id) 刪除使用者

    輸出：
    - redirect(url_for("admin.list_users"))
      附帶 flash("使用者已刪除")
    """
    pass


@admin_bp.route("/recipes", methods=["GET"])
def list_recipes():
    """
    全站食譜管理列表頁面（含私人食譜）。（需管理員）

    GET /admin/recipes

    處理邏輯（待實作）：
    1. 確認管理員身份，否則 abort(403)
    2. Recipe.get_all(public_only=False) 取得全站所有食譜

    輸出：
    - 渲染模板 admin/recipes.html
      context: recipes
    """
    pass


@admin_bp.route("/recipe/<int:id>/delete", methods=["POST"])
def delete_recipe(id):
    """
    管理員強制刪除指定食譜。（需管理員）

    POST /admin/recipe/<int:id>/delete
    URL 參數: id — 食譜 id

    處理邏輯（待實作）：
    1. 確認管理員身份，否則 abort(403)
    2. Recipe.get_by_id(id)，若不存在 → abort(404)
    3. Recipe.delete(id) 刪除食譜

    輸出：
    - redirect(url_for("admin.list_recipes"))
      附帶 flash("食譜已刪除")
    """
    pass
