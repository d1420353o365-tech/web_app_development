"""
app/models/user.py
使用者資料模型，封裝 users 資料表的所有 CRUD 操作。
密碼一律使用 werkzeug.security 進行 hash，絕不明文儲存。
"""

from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from .database import get_db


class User:
    """
    代表 users 資料表的 Model 類別。
    方法皆為 class method，不需實例化即可呼叫。
    """

    # ------------------------------------------------------------------
    # Create
    # ------------------------------------------------------------------

    @classmethod
    def create(cls, username: str, email: str, password: str, is_admin: bool = False) -> int | None:
        """
        建立新使用者。
        - 密碼會在寫入前自動 hash。
        - 若 username 或 email 已存在，回傳 None。

        Args:
            username: 使用者名稱（唯一）
            email:    電子郵件（唯一）
            password: 明文密碼（將被 hash 後儲存）
            is_admin: 是否為管理員，預設 False

        Returns:
            新使用者的 id，若失敗則回傳 None。
        """
        db = get_db()
        password_hash = generate_password_hash(password)
        created_at = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        try:
            cursor = db.execute(
                """
                INSERT INTO users (username, email, password_hash, is_admin, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (username, email, password_hash, int(is_admin), created_at),
            )
            db.commit()
            return cursor.lastrowid
        except Exception:
            db.rollback()
            return None

    # ------------------------------------------------------------------
    # Read
    # ------------------------------------------------------------------

    @classmethod
    def get_all(cls) -> list[dict]:
        """
        取得所有使用者列表（不含密碼 hash）。

        Returns:
            使用者 dict 的 list。
        """
        db = get_db()
        rows = db.execute(
            "SELECT id, username, email, is_admin, created_at FROM users ORDER BY created_at DESC"
        ).fetchall()
        return [dict(row) for row in rows]

    @classmethod
    def get_by_id(cls, user_id: int) -> dict | None:
        """
        依 id 查詢單一使用者（不含密碼 hash）。

        Args:
            user_id: 使用者 id

        Returns:
            使用者 dict，若不存在則回傳 None。
        """
        db = get_db()
        row = db.execute(
            "SELECT id, username, email, is_admin, created_at FROM users WHERE id = ?",
            (user_id,),
        ).fetchone()
        return dict(row) if row else None

    @classmethod
    def get_by_email(cls, email: str) -> dict | None:
        """
        依 email 查詢單一使用者（含密碼 hash，供登入驗證使用）。

        Args:
            email: 電子郵件

        Returns:
            完整使用者 dict（含 password_hash），若不存在則回傳 None。
        """
        db = get_db()
        row = db.execute(
            "SELECT * FROM users WHERE email = ?",
            (email,),
        ).fetchone()
        return dict(row) if row else None

    @classmethod
    def get_by_username(cls, username: str) -> dict | None:
        """
        依 username 查詢單一使用者。

        Args:
            username: 使用者名稱

        Returns:
            使用者 dict，若不存在則回傳 None。
        """
        db = get_db()
        row = db.execute(
            "SELECT id, username, email, is_admin, created_at FROM users WHERE username = ?",
            (username,),
        ).fetchone()
        return dict(row) if row else None

    # ------------------------------------------------------------------
    # Update
    # ------------------------------------------------------------------

    @classmethod
    def update_password(cls, user_id: int, new_password: str) -> bool:
        """
        更新使用者密碼，新密碼會自動 hash。

        Args:
            user_id:      使用者 id
            new_password: 新明文密碼

        Returns:
            True 表示更新成功，False 表示失敗。
        """
        db = get_db()
        new_hash = generate_password_hash(new_password)
        try:
            db.execute(
                "UPDATE users SET password_hash = ? WHERE id = ?",
                (new_hash, user_id),
            )
            db.commit()
            return True
        except Exception:
            db.rollback()
            return False

    # ------------------------------------------------------------------
    # Delete
    # ------------------------------------------------------------------

    @classmethod
    def delete(cls, user_id: int) -> bool:
        """
        刪除指定使用者（CASCADE 會同步刪除該使用者的食譜與收藏）。

        Args:
            user_id: 使用者 id

        Returns:
            True 表示刪除成功，False 表示失敗。
        """
        db = get_db()
        try:
            db.execute("DELETE FROM users WHERE id = ?", (user_id,))
            db.commit()
            return True
        except Exception:
            db.rollback()
            return False

    # ------------------------------------------------------------------
    # 驗證輔助
    # ------------------------------------------------------------------

    @staticmethod
    def verify_password(password_hash: str, password: str) -> bool:
        """
        驗證明文密碼是否與 hash 一致（用於登入驗證）。

        Args:
            password_hash: 資料庫中儲存的 hash 字串
            password:      使用者輸入的明文密碼

        Returns:
            True 表示密碼正確。
        """
        return check_password_hash(password_hash, password)
