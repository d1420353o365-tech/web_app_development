"""
app/routes/auth.py
身分驗證 Blueprint — 處理使用者登入、註冊與登出。

路由清單：
  GET  /auth/login      — 顯示登入表單
  POST /auth/login      — 處理登入邏輯，建立 Session
  GET  /auth/register   — 顯示註冊表單
  POST /auth/register   — 處理註冊邏輯，建立帳號
  POST /auth/logout     — 清除 Session，登出使用者
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash

from app.models.user import User

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


# ---------------------------------------------------------------------------
# 輔助：登入狀態檢查裝飾器（在 implementation 階段實作）
# ---------------------------------------------------------------------------

def login_required(f):
    """裝飾器：確保使用者已登入，否則重導向登入頁。"""
    pass


# ---------------------------------------------------------------------------
# 路由骨架
# ---------------------------------------------------------------------------

@auth_bp.route("/login", methods=["GET"])
def login_page():
    """
    顯示登入表單頁面。

    GET /auth/login

    處理邏輯（待實作）：
    - 若 session 中已有 user_id，重導向首頁（避免重複登入）
    - 渲染 auth/login.html

    輸出：
    - 渲染模板 auth/login.html
    """
    pass


@auth_bp.route("/login", methods=["POST"])
def login():
    """
    處理使用者登入請求。

    POST /auth/login
    表單欄位: email, password

    處理邏輯（待實作）：
    1. 驗證 email 與 password 不為空
    2. User.get_by_email(email) 查詢帳號
    3. User.verify_password(hash, password) 驗證密碼
    4. 成功：將 user_id, username, is_admin 存入 session；重導向首頁
    5. 失敗：flash("帳號或密碼錯誤")；重新渲染登入表單

    輸出：
    - 成功 → redirect(url_for("recipe.index"))
    - 失敗 → 重新渲染 auth/login.html
    """
    pass


@auth_bp.route("/register", methods=["GET"])
def register_page():
    """
    顯示使用者註冊表單頁面。

    GET /auth/register

    處理邏輯（待實作）：
    - 若已登入，重導向首頁
    - 渲染 auth/register.html

    輸出：
    - 渲染模板 auth/register.html
    """
    pass


@auth_bp.route("/register", methods=["POST"])
def register():
    """
    處理使用者註冊請求。

    POST /auth/register
    表單欄位: username, email, password, password_confirm

    處理邏輯（待實作）：
    1. 驗證所有欄位不為空
    2. 確認 password == password_confirm
    3. User.get_by_email(email) 確認 email 尚未被使用
    4. User.create(username, email, password) 建立帳號
    5. 成功：flash("註冊成功，請登入")；重導向登入頁
    6. 失敗：flash(對應錯誤訊息)；重新渲染表單

    輸出：
    - 成功 → redirect(url_for("auth.login_page"))
    - 失敗 → 重新渲染 auth/register.html
    """
    pass


@auth_bp.route("/logout", methods=["POST"])
def logout():
    """
    處理使用者登出請求。

    POST /auth/logout

    處理邏輯（待實作）：
    1. session.clear() 清除所有 Session 資料
    2. flash("已成功登出")
    3. 重導向首頁

    輸出：
    - redirect(url_for("recipe.index"))
    """
    pass
