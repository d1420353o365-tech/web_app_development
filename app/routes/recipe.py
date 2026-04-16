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

from app.models.recipe import Recipe
from app.models.ingredient import Ingredient
from app.models.favorite import Favorite

recipe_bp = Blueprint("recipe", __name__)


# ---------------------------------------------------------------------------
# 路由骨架
# ---------------------------------------------------------------------------

@recipe_bp.route("/")
def index():
    """
    首頁：顯示公開食譜列表，支援關鍵字搜尋。

    GET /
    Query String: ?q=關鍵字（可選）

    處理邏輯（待實作）：
    1. 取得 request.args.get("q", "") 搜尋字串
    2. 若有關鍵字：Recipe.search_by_keyword(q)
       若無：Recipe.get_all(public_only=True)
    3. 渲染模板，傳入 recipes list 與 query 字串

    輸出：
    - 渲染模板 recipe/index.html
      context: recipes, query
    """
    pass


@recipe_bp.route("/recipe/search", methods=["GET"])
def ingredient_search():
    """
    食材組合搜尋頁：依使用者勾選的食材篩選包含所有指定食材的食譜。

    GET /recipe/search
    Query String: ?ingredients=雞蛋&ingredients=番茄（可多選）

    處理邏輯（待實作）：
    1. Ingredient.get_all() 取得所有食材（供勾選清單顯示）
    2. request.args.getlist("ingredients") 取得已選食材名稱
    3. 若有選食材：Recipe.search_by_ingredients(selected_names)
       若無：results 為空 list
    4. 渲染模板，傳入 all_ingredients、results、selected

    輸出：
    - 渲染模板 recipe/search.html
      context: all_ingredients, results, selected
    """
    pass


@recipe_bp.route("/recipe/add", methods=["GET"])
def add_recipe_page():
    """
    顯示新增食譜表單頁面。（需登入）

    GET /recipe/add

    處理邏輯（待實作）：
    1. 確認 session 中有 user_id，否則重導向登入頁
    2. Ingredient.get_all() 取得所有食材（供自動完成）
    3. 渲染表單，傳入空白 recipe dict 與 all_ingredients

    輸出：
    - 渲染模板 recipe/form.html
      context: recipe={}, all_ingredients, is_edit=False
    - 未登入 → redirect(url_for("auth.login_page"))
    """
    pass


@recipe_bp.route("/recipe/add", methods=["POST"])
def add_recipe():
    """
    處理新增食譜提交。（需登入）

    POST /recipe/add
    表單欄位:
      - title:               食譜名稱（必填）
      - description:         食譜簡介
      - steps[]:             步驟陣列（多行 textarea 或多個 input）
      - category:            分類
      - difficulty:          難易度（easy/medium/hard）
      - cook_time_minutes:   料理時間（分鐘）
      - is_public:           公開狀態（checkbox）
      - ingredient_name[]:   食材名稱陣列
      - ingredient_quantity[]: 食材用量陣列（與名稱一一對應）

    處理邏輯（待實作）：
    1. 確認已登入
    2. 驗證 title 與 steps 不為空
    3. 組合 ingredients = [{"name":..., "quantity":...}, ...]
    4. Recipe.create(user_id, title, steps, ..., ingredients) 建立食譜
    5. 成功：重導向至 /recipe/<new_id>
    6. 失敗：flash(錯誤訊息)；重新渲染表單

    輸出：
    - 成功 → redirect(url_for("recipe.detail", id=new_id))
    - 失敗 → 重新渲染 recipe/form.html
    """
    pass


@recipe_bp.route("/recipe/<int:id>", methods=["GET"])
def detail(id):
    """
    食譜詳細頁面：顯示完整食譜資訊（食材、步驟）與收藏狀態。

    GET /recipe/<int:id>
    URL 參數: id — 食譜 id

    處理邏輯（待實作）：
    1. Recipe.get_by_id(id)，若不存在 → abort(404)
    2. 若食譜為私人（is_public=0）且目前使用者非作者 → abort(403)
    3. 若已登入：Favorite.is_favorited(session["user_id"], id)
    4. Favorite.get_count_by_recipe(id) 取得收藏總數

    輸出：
    - 渲染模板 recipe/detail.html
      context: recipe, is_favorited, fav_count
    """
    pass


@recipe_bp.route("/recipe/<int:id>/edit", methods=["GET"])
def edit_recipe_page(id):
    """
    顯示編輯食譜表單（需登入且為食譜作者或管理員）。

    GET /recipe/<int:id>/edit
    URL 參數: id — 食譜 id

    處理邏輯（待實作）：
    1. 確認已登入，否則重導向登入頁
    2. Recipe.get_by_id(id)，若不存在 → abort(404)
    3. 確認 user_id == recipe["user_id"] 或 session["is_admin"]，否則 abort(403)
    4. Ingredient.get_all() 取得所有食材

    輸出：
    - 渲染模板 recipe/form.html
      context: recipe（含現有食材）, all_ingredients, is_edit=True
    """
    pass


@recipe_bp.route("/recipe/<int:id>/edit", methods=["POST"])
def edit_recipe(id):
    """
    處理食譜編輯提交（需登入且為食譜作者或管理員）。

    POST /recipe/<int:id>/edit
    表單欄位: 同 add_recipe（POST /recipe/add）

    處理邏輯（待實作）：
    1. 確認已登入及作者身份
    2. 驗證必填欄位
    3. Recipe.update(id, ...) 更新食譜
    4. 成功：重導向至 /recipe/<id>
    5. 失敗：flash(錯誤訊息)；重新渲染編輯表單

    輸出：
    - 成功 → redirect(url_for("recipe.detail", id=id))
    - 失敗 → 重新渲染 recipe/form.html
    """
    pass


@recipe_bp.route("/recipe/<int:id>/delete", methods=["POST"])
def delete_recipe(id):
    """
    刪除指定食譜（需登入且為作者或管理員）。

    POST /recipe/<int:id>/delete
    URL 參數: id — 食譜 id

    處理邏輯（待實作）：
    1. 確認已登入
    2. Recipe.get_by_id(id)，若不存在 → abort(404)
    3. 確認 user_id == recipe["user_id"] 或 is_admin，否則 abort(403)
    4. Recipe.delete(id) 刪除食譜

    輸出：
    - 成功 → redirect(url_for("recipe.index"))
      附帶 flash("食譜已刪除")
    """
    pass


@recipe_bp.route("/recipe/<int:id>/favorite", methods=["POST"])
def toggle_favorite(id):
    """
    切換登入使用者對指定食譜的收藏狀態。（需登入，回傳 JSON）

    POST /recipe/<int:id>/favorite
    URL 參數: id — 食譜 id

    處理邏輯（待實作）：
    1. 確認已登入，否則回傳 JSON {"error": "請先登入", "redirect": "/auth/login"}，HTTP 401
    2. Favorite.toggle(session["user_id"], id) 切換收藏狀態
    3. Favorite.get_count_by_recipe(id) 取得最新收藏數

    輸出：
    - 成功 → JSON {"status": "added"|"removed", "fav_count": <int>}
    - 未登入 → JSON {"error": "請先登入", "redirect": "/auth/login"}，HTTP 401
    """
    pass
