"""
app/models/ingredient.py
食材資料模型，封裝 ingredients 資料表的 CRUD 操作。
全站食材統一管理，透過 recipe_ingredients 中間表與食譜建立多對多關聯。
"""

from .database import get_db


class Ingredient:
    """
    代表 ingredients 資料表的 Model 類別。
    """

    # ------------------------------------------------------------------
    # Create
    # ------------------------------------------------------------------

    @classmethod
    def get_or_create(cls, name: str) -> int:
        """
        若食材名稱已存在則取得其 id，否則建立後回傳新 id。
        這是新增食譜時關聯食材的主要入口，確保食材不重複。

        Args:
            name: 食材名稱（會去除首尾空白）

        Returns:
            食材的 id。
        """
        name = name.strip()
        db = get_db()
        row = db.execute(
            "SELECT id FROM ingredients WHERE name = ?", (name,)
        ).fetchone()
        if row:
            return row["id"]
        cursor = db.execute(
            "INSERT INTO ingredients (name) VALUES (?)", (name,)
        )
        db.commit()
        return cursor.lastrowid

    @classmethod
    def create(cls, name: str) -> int | None:
        """
        直接建立新食材。若名稱已存在則回傳 None。
        一般情況建議使用 get_or_create()。

        Args:
            name: 食材名稱

        Returns:
            新食材的 id，若已存在則回傳 None。
        """
        db = get_db()
        try:
            cursor = db.execute(
                "INSERT INTO ingredients (name) VALUES (?)", (name.strip(),)
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
        取得所有食材（依名稱排序），供食材搜尋頁面的勾選清單使用。

        Returns:
            食材 dict 的 list，欄位: id, name。
        """
        db = get_db()
        rows = db.execute(
            "SELECT id, name FROM ingredients ORDER BY name ASC"
        ).fetchall()
        return [dict(row) for row in rows]

    @classmethod
    def get_by_id(cls, ingredient_id: int) -> dict | None:
        """
        依 id 查詢單一食材。

        Args:
            ingredient_id: 食材 id

        Returns:
            食材 dict，若不存在則回傳 None。
        """
        db = get_db()
        row = db.execute(
            "SELECT id, name FROM ingredients WHERE id = ?", (ingredient_id,)
        ).fetchone()
        return dict(row) if row else None

    @classmethod
    def get_by_name(cls, name: str) -> dict | None:
        """
        依名稱查詢食材（完全匹配）。

        Args:
            name: 食材名稱

        Returns:
            食材 dict，若不存在則回傳 None。
        """
        db = get_db()
        row = db.execute(
            "SELECT id, name FROM ingredients WHERE name = ?", (name.strip(),)
        ).fetchone()
        return dict(row) if row else None

    @classmethod
    def search_by_name(cls, keyword: str) -> list[dict]:
        """
        模糊搜尋食材名稱，供前端自動完成建議使用。

        Args:
            keyword: 搜尋關鍵字

        Returns:
            符合條件的食材 dict list。
        """
        db = get_db()
        rows = db.execute(
            "SELECT id, name FROM ingredients WHERE name LIKE ? ORDER BY name ASC",
            (f"%{keyword.strip()}%",),
        ).fetchall()
        return [dict(row) for row in rows]

    # ------------------------------------------------------------------
    # Update
    # ------------------------------------------------------------------

    @classmethod
    def update(cls, ingredient_id: int, name: str) -> bool:
        """
        更新食材名稱。

        Args:
            ingredient_id: 食材 id
            name:          新名稱

        Returns:
            True 表示成功，False 表示失敗（如名稱已被使用）。
        """
        db = get_db()
        try:
            db.execute(
                "UPDATE ingredients SET name = ? WHERE id = ?",
                (name.strip(), ingredient_id),
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
    def delete(cls, ingredient_id: int) -> bool:
        """
        刪除食材（CASCADE 會同步移除 recipe_ingredients 中的關聯）。

        Args:
            ingredient_id: 食材 id

        Returns:
            True 表示成功，False 表示失敗。
        """
        db = get_db()
        try:
            db.execute(
                "DELETE FROM ingredients WHERE id = ?", (ingredient_id,)
            )
            db.commit()
            return True
        except Exception:
            db.rollback()
            return False
