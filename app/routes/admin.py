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
from functools import wraps

from app.models.user import User
from app.models.recipe import Recipe

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


# ---------------------------------------------------------------------------
# 輔助：管理員權限檢查
# ---------------------------------------------------------------------------

def admin_required(f):
    """裝飾器：確認使用者具有管理員身份，否則 abort(403)。"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("is_admin"):
            abort(403)
        return f(*args, **kwargs)
    return decorated_function


# ---------------------------------------------------------------------------
# 路由實作
# ---------------------------------------------------------------------------

@admin_bp.route("/", methods=["GET"])
@admin_required
def dashboard():
    """管理後台總覽面板。"""
    users = User.get_all()
    all_recipes = Recipe.get_all(public_only=False)
    
    user_count = len(users)
    recipe_count = len(all_recipes)
    recent_recipes = all_recipes[:5]
    
    return render_template("admin/dashboard.html", user_count=user_count, recipe_count=recipe_count, recent_recipes=recent_recipes)


@admin_bp.route("/users", methods=["GET"])
@admin_required
def list_users():
    """使用者管理列表頁面。"""
    users = User.get_all()
    return render_template("admin/users.html", users=users)


@admin_bp.route("/users/<int:id>/delete", methods=["POST"])
@admin_required
def delete_user(id):
    """強制刪除使用者帳號。"""
    user = User.get_by_id(id)
    if not user:
        abort(404)
        
    if user["id"] == session["user_id"]:
        flash("您無法刪除自己的帳號！", "danger")
        return redirect(url_for("admin.list_users"))
        
    User.delete(id)
    flash("使用者已刪除", "success")
    return redirect(url_for("admin.list_users"))


@admin_bp.route("/recipes", methods=["GET"])
@admin_required
def list_recipes():
    """全站食譜管理列表頁面。"""
    recipes = Recipe.get_all(public_only=False)
    return render_template("admin/recipes.html", recipes=recipes)


@admin_bp.route("/recipe/<int:id>/delete", methods=["POST"])
@admin_required
def delete_recipe(id):
    """管理員強制刪除指定食譜。"""
    recipe = Recipe.get_by_id(id)
    if not recipe:
        abort(404)
        
    Recipe.delete(id)
    flash("食譜已強制刪除", "success")
    return redirect(url_for("admin.list_recipes"))
