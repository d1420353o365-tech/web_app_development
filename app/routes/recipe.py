"""
app/routes/recipe.py
食譜 Blueprint — 處理食譜的 CRUD、關鍵字搜尋、食材組合搜尋與收藏切換。

路由清單：
  GET  /                         — 首頁，顯示公開食譜列表，支援 ?q= 關鍵字搜尋
  GET  /recipe/search            — 食材組合搜尋頁（勾選食材 → 篩選食譜）
  GET  /recipe/add               — 新增食譜表單（需登入）
  POST /recipe/add               — 處理新增食譜（需登入）
  GET  /recipe/<int:id>          — 食譜詳細頁面
  GET  /recipe/<int:id>/edit     — 編輯食譜表單（需登入且為作者）
  POST /recipe/<int:id>/edit     — 處理編輯食譜（需登入且為作者）
  POST /recipe/<int:id>/delete   — 刪除食譜（需登入且為作者或管理員）
  POST /recipe/<int:id>/favorite — 切換收藏狀態（需登入），回傳 JSON
"""

from flask import (
    Blueprint, render_template, request, redirect,
    url_for, session, flash, abort, jsonify
)
import json

from app.models.recipe import Recipe
from app.models.ingredient import Ingredient
from app.models.favorite import Favorite
from app.routes.auth import login_required

recipe_bp = Blueprint("recipe", __name__)


# ---------------------------------------------------------------------------
# 路由實作
# ---------------------------------------------------------------------------

@recipe_bp.route("/")
def index():
    """首頁：顯示公開食譜列表，支援關鍵字搜尋。"""
    query = request.args.get("q", "").strip()
    if query:
        recipes = Recipe.search_by_keyword(query)
    else:
        recipes = Recipe.get_all(public_only=True)
    return render_template("recipe/index.html", recipes=recipes, query=query)


@recipe_bp.route("/recipe/search", methods=["GET"])
def ingredient_search():
    """食材組合搜尋頁：依使用者勾選的食材篩選食譜。"""
    all_ingredients = Ingredient.get_all()
    selected = request.args.getlist("ingredients")
    results = []
    
    if selected:
        results = Recipe.search_by_ingredients(selected)
        
    return render_template("recipe/search.html", all_ingredients=all_ingredients, results=results, selected=selected)


@recipe_bp.route("/recipe/add", methods=["GET"])
@login_required
def add_recipe_page():
    """顯示新增食譜表單頁面。"""
    all_ingredients = Ingredient.get_all()
    return render_template("recipe/form.html", recipe={}, all_ingredients=all_ingredients, is_edit=False)


@recipe_bp.route("/recipe/add", methods=["POST"])
@login_required
def add_recipe():
    """處理新增食譜提交。"""
    title = request.form.get("title", "").strip()
    description = request.form.get("description", "")
    steps = [s.strip() for s in request.form.getlist("steps[]") if s.strip()]
    category = request.form.get("category", "")
    difficulty = request.form.get("difficulty", "")
    
    cook_time = request.form.get("cook_time_minutes")
    cook_time_minutes = int(cook_time) if cook_time and cook_time.isdigit() else None
    
    is_public = request.form.get("is_public") == "on"
    
    ing_names = request.form.getlist("ingredient_name[]")
    ing_quants = request.form.getlist("ingredient_quantity[]")
    
    ingredients = []
    for name, quantity in zip(ing_names, ing_quants):
        if name.strip():
            ingredients.append({"name": name.strip(), "quantity": quantity.strip()})

    if not title or not steps:
        flash("請填寫食譜名稱與至少一個步驟", "danger")
        return redirect(url_for('recipe.add_recipe_page'))

    recipe_id = Recipe.create(
        user_id=session["user_id"],
        title=title,
        steps=steps,
        description=description,
        category=category,
        difficulty=difficulty,
        cook_time_minutes=cook_time_minutes,
        is_public=is_public,
        ingredients=ingredients
    )
    
    if recipe_id:
        flash("新食譜建立成功！", "success")
        return redirect(url_for("recipe.detail", id=recipe_id))
    else:
        flash("建立失敗，請稍後再試", "danger")
        return redirect(url_for("recipe.add_recipe_page"))


@recipe_bp.route("/recipe/<int:id>", methods=["GET"])
def detail(id):
    """食譜詳細頁面。"""
    recipe = Recipe.get_by_id(id)
    if not recipe:
        abort(404)
        
    is_author_or_admin = session.get("user_id") == recipe["user_id"] or session.get("is_admin")
    if not recipe["is_public"] and not is_author_or_admin:
        abort(403)
        
    is_fav = False
    if "user_id" in session:
        is_fav = Favorite.is_favorited(session["user_id"], id)
        
    fav_count = Favorite.get_count_by_recipe(id)
    
    return render_template("recipe/detail.html", recipe=recipe, is_favorited=is_fav, fav_count=fav_count)


@recipe_bp.route("/recipe/<int:id>/edit", methods=["GET"])
@login_required
def edit_recipe_page(id):
    """顯示編輯食譜表單。"""
    recipe = Recipe.get_by_id(id)
    if not recipe:
        abort(404)
        
    if session["user_id"] != recipe["user_id"] and not session.get("is_admin"):
        abort(403)
        
    all_ingredients = Ingredient.get_all()
    return render_template("recipe/form.html", recipe=recipe, all_ingredients=all_ingredients, is_edit=True)


@recipe_bp.route("/recipe/<int:id>/edit", methods=["POST"])
@login_required
def edit_recipe(id):
    """處理食譜編輯提交。"""
    recipe = Recipe.get_by_id(id)
    if not recipe:
        abort(404)
        
    if session["user_id"] != recipe["user_id"] and not session.get("is_admin"):
        abort(403)

    title = request.form.get("title", "").strip()
    description = request.form.get("description", "")
    steps = [s.strip() for s in request.form.getlist("steps[]") if s.strip()]
    category = request.form.get("category", "")
    difficulty = request.form.get("difficulty", "")
    
    cook_time = request.form.get("cook_time_minutes")
    cook_time_minutes = int(cook_time) if cook_time and cook_time.isdigit() else None
    
    is_public = request.form.get("is_public") == "on"
    
    ing_names = request.form.getlist("ingredient_name[]")
    ing_quants = request.form.getlist("ingredient_quantity[]")
    
    ingredients = []
    for name, quantity in zip(ing_names, ing_quants):
        if name.strip():
            ingredients.append({"name": name.strip(), "quantity": quantity.strip()})

    if not title or not steps:
        flash("請填寫食譜名稱與至少一個步驟", "danger")
        return redirect(url_for('recipe.edit_recipe_page', id=id))

    success = Recipe.update(
        recipe_id=id,
        title=title,
        steps=steps,
        description=description,
        category=category,
        difficulty=difficulty,
        cook_time_minutes=cook_time_minutes,
        is_public=is_public,
        ingredients=ingredients
    )
    
    if success:
        flash("食譜更新成功！", "success")
        return redirect(url_for("recipe.detail", id=id))
    else:
        flash("更新失敗，請稍後再試", "danger")
        return redirect(url_for("recipe.edit_recipe_page", id=id))


@recipe_bp.route("/recipe/<int:id>/delete", methods=["POST"])
@login_required
def delete_recipe(id):
    """刪除指定食譜。"""
    recipe = Recipe.get_by_id(id)
    if not recipe:
        abort(404)
        
    if session["user_id"] != recipe["user_id"] and not session.get("is_admin"):
        abort(403)
        
    if Recipe.delete(id):
        flash("食譜已刪除", "success")
    else:
        flash("刪除失敗", "danger")
        
    return redirect(url_for("recipe.index"))


@recipe_bp.route("/recipe/<int:id>/favorite", methods=["POST"])
def toggle_favorite(id):
    """切換收藏狀態（回傳 JSON）。"""
    if "user_id" not in session:
        return jsonify({"error": "請先登入", "redirect": url_for("auth.login_page")}), 401
        
    status = Favorite.toggle(session["user_id"], id)
    fav_count = Favorite.get_count_by_recipe(id)
    
    return jsonify({"status": status, "fav_count": fav_count})
