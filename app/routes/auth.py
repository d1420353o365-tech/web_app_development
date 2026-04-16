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

from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, session, flash

from app.models.user import User

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


# ---------------------------------------------------------------------------
# 輔助：登入狀態檢查裝飾器
# ---------------------------------------------------------------------------

def login_required(f):
    """裝飾器：確保使用者已登入，否則重導向登入頁。"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("請先登入", "warning")
            return redirect(url_for("auth.login_page"))
        return f(*args, **kwargs)
    return decorated_function


# ---------------------------------------------------------------------------
# 路由實作
# ---------------------------------------------------------------------------

@auth_bp.route("/login", methods=["GET"])
def login_page():
    """顯示登入表單頁面。"""
    if "user_id" in session:
        return redirect(url_for("recipe.index"))
    return render_template("auth/login.html")


@auth_bp.route("/login", methods=["POST"])
def login():
    """處理使用者登入請求。"""
    email = request.form.get("email", "").strip()
    password = request.form.get("password", "")

    if not email or not password:
        flash("請輸入電子郵件與密碼", "danger")
        return render_template("auth/login.html")

    user = User.get_by_email(email)
    if user and User.verify_password(user["password_hash"], password):
        session["user_id"] = user["id"]
        session["username"] = user["username"]
        session["is_admin"] = bool(user["is_admin"])
        flash("登入成功！", "success")
        return redirect(url_for("recipe.index"))
    else:
        flash("帳號或密碼錯誤", "danger")
        return render_template("auth/login.html")


@auth_bp.route("/register", methods=["GET"])
def register_page():
    """顯示使用者註冊表單頁面。"""
    if "user_id" in session:
        return redirect(url_for("recipe.index"))
    return render_template("auth/register.html")


@auth_bp.route("/register", methods=["POST"])
def register():
    """處理使用者註冊請求。"""
    username = request.form.get("username", "").strip()
    email = request.form.get("email", "").strip()
    password = request.form.get("password", "")
    password_confirm = request.form.get("password_confirm", "")

    if not username or not email or not password or not password_confirm:
        flash("請填寫所有必填欄位", "danger")
        return render_template("auth/register.html")

    if password != password_confirm:
        flash("兩次密碼輸入不一致", "danger")
        return render_template("auth/register.html")

    if User.get_by_email(email):
        flash("此電子郵件已被註冊", "danger")
        return render_template("auth/register.html")

    if User.get_by_username(username):
        flash("此使用者名稱已被使用", "danger")
        return render_template("auth/register.html")

    user_id = User.create(username, email, password)
    if user_id:
        flash("註冊成功，請登入", "success")
        return redirect(url_for("auth.login_page"))
    else:
        flash("註冊發生錯誤，請稍後再試", "danger")
        return render_template("auth/register.html")


@auth_bp.route("/logout", methods=["POST"])
def logout():
    """處理使用者登出請求。"""
    session.clear()
    flash("已成功登出", "success")
    return redirect(url_for("recipe.index"))
