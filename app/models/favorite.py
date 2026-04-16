"""
app/models/favorite.py
使用者收藏資料模型，封裝 favorites 資料表的操作。
提供收藏/取消收藏（切換邏輯）與查詢個人收藏清單功能。
"""

from datetime import datetime
from .database import get_db


class Favorite:
    """
    代表 favorites 資料表的 Model 類別。
    """

    # ------------------------------------------------------------------
    # Create / Toggle
    # ------------------------------------------------------------------

    @classmethod
    def toggle(cls, user_id: int, recipe_id: int) -> str:
        """
        切換收藏狀態：若已收藏則取消，若未收藏則新增。
        適合用於「收藏/取消收藏」按鈕的後端邏輯。

        Args:
            user_id:   使用者 id
            recipe_id: 食譜 id

        Returns:
            "added"   表示新增收藏成功
            "removed" 表示取消收藏成功
            "error"   表示操作失敗
        """
        db = get_db()
        existing = db.execute(
            "SELECT id FROM favorites WHERE user_id = ? AND recipe_id = ?",
            (user_id, recipe_id),
        ).fetchone()

        try:
            if existing:
                db.execute(
                    "DELETE FROM favorites WHERE user_id = ? AND recipe_id = ?",
                    (user_id, recipe_id),
                )
                db.commit()
                return "removed"
            else:
                created_at = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
                db.execute(
                    "INSERT INTO favorites (user_id, recipe_id, created_at) VALUES (?, ?, ?)",
                    (user_id, recipe_id, created_at),
                )
                db.commit()
                return "added"
        except Exception:
            db.rollback()
            return "error"

    @classmethod
    def add(cls, user_id: int, recipe_id: int) -> bool:
        """
        新增收藏（若已存在則忽略）。

        Args:
            user_id:   使用者 id
            recipe_id: 食譜 id

        Returns:
            True 表示成功（含已存在情況），False 表示失敗。
        """
        db = get_db()
        created_at = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        try:
            db.execute(
                "INSERT OR IGNORE INTO favorites (user_id, recipe_id, created_at) VALUES (?, ?, ?)",
                (user_id, recipe_id, created_at),
            )
            db.commit()
            return True
        except Exception:
            db.rollback()
            return False

    # ------------------------------------------------------------------
    # Read
    # ------------------------------------------------------------------

    @classmethod
    def get_all(cls) -> list[dict]:
        """
        取得全站所有收藏記錄（管理員用途）。

        Returns:
            收藏 dict 的 list。
        """
        db = get_db()
        rows = db.execute(
            "SELECT * FROM favorites ORDER BY created_at DESC"
        ).fetchall()
        return [dict(row) for row in rows]

    @classmethod
    def get_by_id(cls, favorite_id: int) -> dict | None:
        """
        依 id 查詢單一收藏記錄。

        Args:
            favorite_id: 收藏 id

        Returns:
            收藏 dict，若不存在則回傳 None。
        """
        db = get_db()
        row = db.execute(
            "SELECT * FROM favorites WHERE id = ?", (favorite_id,)
        ).fetchone()
        return dict(row) if row else None

    @classmethod
    def get_by_user(cls, user_id: int) -> list[dict]:
        """
        取得特定使用者的所有收藏食譜（含食譜基本資訊）。
        用於「我的收藏清單」頁面。

        Args:
            user_id: 使用者 id

        Returns:
            包含食譜資訊的收藏 dict list，欄位含:
            favorite_id, recipe_id, title, category, cover_image,
            author, cook_time_minutes, favorited_at。
        """
        db = get_db()
        rows = db.execute(
            """
            SELECT
                f.id         AS favorite_id,
                f.created_at AS favorited_at,
                r.id         AS recipe_id,
                r.title,
                r.category,
                r.difficulty,
                r.cook_time_minutes,
                r.cover_image,
                u.username   AS author
            FROM favorites f
            JOIN recipes r ON f.recipe_id = r.id
            JOIN users u   ON r.user_id = u.id
            WHERE f.user_id = ?
            ORDER BY f.created_at DESC
            """,
            (user_id,),
        ).fetchall()
        return [dict(row) for row in rows]

    @classmethod
    def is_favorited(cls, user_id: int, recipe_id: int) -> bool:
        """
        確認指定使用者是否已收藏某食譜。
        用於食譜詳細頁顯示收藏按鈕狀態。

        Args:
            user_id:   使用者 id
            recipe_id: 食譜 id

        Returns:
            True 表示已收藏，False 表示未收藏。
        """
        db = get_db()
        row = db.execute(
            "SELECT id FROM favorites WHERE user_id = ? AND recipe_id = ?",
            (user_id, recipe_id),
        ).fetchone()
        return row is not None

    @classmethod
    def get_count_by_recipe(cls, recipe_id: int) -> int:
        """
        取得特定食譜的收藏數量。

        Args:
            recipe_id: 食譜 id

        Returns:
            收藏數量（整數）。
        """
        db = get_db()
        row = db.execute(
            "SELECT COUNT(*) AS cnt FROM favorites WHERE recipe_id = ?",
            (recipe_id,),
        ).fetchone()
        return row["cnt"] if row else 0

    # ------------------------------------------------------------------
    # Delete
    # ------------------------------------------------------------------

    @classmethod
    def remove(cls, user_id: int, recipe_id: int) -> bool:
        """
        移除指定使用者對某食譜的收藏。

        Args:
            user_id:   使用者 id
            recipe_id: 食譜 id

        Returns:
            True 表示成功，False 表示失敗。
        """
        db = get_db()
        try:
            db.execute(
                "DELETE FROM favorites WHERE user_id = ? AND recipe_id = ?",
                (user_id, recipe_id),
            )
            db.commit()
            return True
        except Exception:
            db.rollback()
            return False

    @classmethod
    def delete(cls, favorite_id: int) -> bool:
        """
        依收藏 id 刪除記錄。

        Args:
            favorite_id: 收藏 id

        Returns:
            True 表示成功，False 表示失敗。
        """
        db = get_db()
        try:
            db.execute("DELETE FROM favorites WHERE id = ?", (favorite_id,))
            db.commit()
            return True
        except Exception:
            db.rollback()
            return False
