"""
app/models/recipe.py
食譜資料模型，封裝 recipes 與 recipe_ingredients 資料表的操作。
這是系統最核心的 Model，包含：
  - 食譜 CRUD
  - 以食材組合搜尋食譜（核心功能）
  - 關鍵字搜尋
  - 食材關聯管理
"""

import json
from datetime import datetime
from .database import get_db
from .ingredient import Ingredient


class Recipe:
    """
    代表 recipes 資料表的 Model 類別。
    同時管理 recipe_ingredients 中間表的關聯操作。
    """

    # ------------------------------------------------------------------
    # Create
    # ------------------------------------------------------------------

    @classmethod
    def create(
        cls,
        user_id: int,
        title: str,
        steps: list[str],
        description: str = None,
        category: str = None,
        difficulty: str = None,
        cook_time_minutes: int = None,
        is_public: bool = True,
        cover_image: str = None,
        ingredients: list[dict] = None,
    ) -> int | None:
        """
        建立新食譜，同時寫入食材關聯。

        Args:
            user_id:           建立者的使用者 id
            title:             食譜名稱
            steps:             料理步驟（Python list，會轉為 JSON 儲存）
            description:       食譜簡介
            category:          分類（如: 家常 / 甜點 / 健身）
            difficulty:        難易度（easy / medium / hard）
            cook_time_minutes: 預計料理時間（分鐘）
            is_public:         是否公開，預設 True
            cover_image:       封面圖片路徑
            ingredients:       食材清單，格式為 [{"name": "雞蛋", "quantity": "2顆"}, ...]

        Returns:
            新食譜的 id，若失敗則回傳 None。
        """
        db = get_db()
        now = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        steps_json = json.dumps(steps, ensure_ascii=False)

        try:
            cursor = db.execute(
                """
                INSERT INTO recipes
                    (user_id, title, description, steps, category, difficulty,
                     cook_time_minutes, is_public, cover_image, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    user_id, title, description, steps_json, category, difficulty,
                    cook_time_minutes, int(is_public), cover_image, now, now,
                ),
            )
            recipe_id = cursor.lastrowid

            # 寫入食材關聯
            if ingredients:
                cls._save_ingredients(db, recipe_id, ingredients)

            db.commit()
            return recipe_id
        except Exception:
            db.rollback()
            return None

    # ------------------------------------------------------------------
    # Read
    # ------------------------------------------------------------------

    @classmethod
    def get_all(cls, public_only: bool = True) -> list[dict]:
        """
        取得食譜列表，依建立時間降序排列。

        Args:
            public_only: 是否只取公開食譜，預設 True

        Returns:
            食譜 dict 的 list（含作者 username，不含詳細食材）。
        """
        db = get_db()
        where = "WHERE r.is_public = 1" if public_only else ""
        rows = db.execute(
            f"""
            SELECT r.*, u.username AS author
            FROM recipes r
            JOIN users u ON r.user_id = u.id
            {where}
            ORDER BY r.created_at DESC
            """
        ).fetchall()
        return [cls._parse_row(row) for row in rows]

    @classmethod
    def get_by_id(cls, recipe_id: int) -> dict | None:
        """
        依 id 取得單一食譜（含完整食材清單與步驟）。

        Args:
            recipe_id: 食譜 id

        Returns:
            食譜完整 dict，若不存在則回傳 None。
        """
        db = get_db()
        row = db.execute(
            """
            SELECT r.*, u.username AS author
            FROM recipes r
            JOIN users u ON r.user_id = u.id
            WHERE r.id = ?
            """,
            (recipe_id,),
        ).fetchone()
        if not row:
            return None
        recipe = cls._parse_row(row)
        recipe["ingredients"] = cls.get_ingredients(recipe_id)
        return recipe

    @classmethod
    def get_by_user(cls, user_id: int) -> list[dict]:
        """
        取得特定使用者建立的所有食譜。

        Args:
            user_id: 使用者 id

        Returns:
            食譜 dict 的 list。
        """
        db = get_db()
        rows = db.execute(
            """
            SELECT r.*, u.username AS author
            FROM recipes r
            JOIN users u ON r.user_id = u.id
            WHERE r.user_id = ?
            ORDER BY r.created_at DESC
            """,
            (user_id,),
        ).fetchall()
        return [cls._parse_row(row) for row in rows]

    @classmethod
    def search_by_keyword(cls, keyword: str, public_only: bool = True) -> list[dict]:
        """
        依關鍵字搜尋食譜名稱（模糊搜尋）。

        Args:
            keyword:    搜尋關鍵字
            public_only: 是否只搜尋公開食譜

        Returns:
            符合條件的食譜 dict list。
        """
        db = get_db()
        where_public = "AND r.is_public = 1" if public_only else ""
        rows = db.execute(
            f"""
            SELECT r.*, u.username AS author
            FROM recipes r
            JOIN users u ON r.user_id = u.id
            WHERE r.title LIKE ?
            {where_public}
            ORDER BY r.created_at DESC
            """,
            (f"%{keyword.strip()}%",),
        ).fetchall()
        return [cls._parse_row(row) for row in rows]

    @classmethod
    def search_by_ingredients(cls, ingredient_names: list[str], public_only: bool = True) -> list[dict]:
        """
        【核心功能】依食材組合搜尋食譜：
        回傳「同時包含所有指定食材」的食譜（AND 邏輯）。
        使用 GROUP BY + HAVING COUNT 實作交集查詢，支援良好的擴充性。

        Args:
            ingredient_names: 食材名稱 list，如: ["雞蛋", "番茄"]
            public_only:      是否只搜尋公開食譜

        Returns:
            符合條件的食譜 dict list。
        """
        if not ingredient_names:
            return []

        db = get_db()
        count = len(ingredient_names)
        placeholders = ",".join("?" * count)
        where_public = "AND r.is_public = 1" if public_only else ""

        rows = db.execute(
            f"""
            SELECT r.*, u.username AS author
            FROM recipes r
            JOIN users u ON r.user_id = u.id
            WHERE r.id IN (
                SELECT ri.recipe_id
                FROM recipe_ingredients ri
                JOIN ingredients i ON ri.ingredient_id = i.id
                WHERE i.name IN ({placeholders})
                {where_public.replace("r.", "AND r.")}
                GROUP BY ri.recipe_id
                HAVING COUNT(DISTINCT i.id) = ?
            )
            ORDER BY r.created_at DESC
            """,
            (*ingredient_names, count),
        ).fetchall()
        return [cls._parse_row(row) for row in rows]

    @classmethod
    def get_ingredients(cls, recipe_id: int) -> list[dict]:
        """
        取得指定食譜的所有食材（含用量）。

        Args:
            recipe_id: 食譜 id

        Returns:
            食材 dict list，欄位: ingredient_id, name, quantity。
        """
        db = get_db()
        rows = db.execute(
            """
            SELECT i.id AS ingredient_id, i.name, ri.quantity
            FROM recipe_ingredients ri
            JOIN ingredients i ON ri.ingredient_id = i.id
            WHERE ri.recipe_id = ?
            ORDER BY i.name ASC
            """,
            (recipe_id,),
        ).fetchall()
        return [dict(row) for row in rows]

    # ------------------------------------------------------------------
    # Update
    # ------------------------------------------------------------------

    @classmethod
    def update(
        cls,
        recipe_id: int,
        title: str = None,
        description: str = None,
        steps: list[str] = None,
        category: str = None,
        difficulty: str = None,
        cook_time_minutes: int = None,
        is_public: bool = None,
        cover_image: str = None,
        ingredients: list[dict] = None,
    ) -> bool:
        """
        更新食譜資料。只更新傳入的非 None 欄位。
        若傳入 ingredients 則重建所有食材關聯。

        Args:
            recipe_id: 食譜 id
            (其餘同 create() 參數說明)

        Returns:
            True 表示成功，False 表示失敗或食譜不存在。
        """
        db = get_db()
        fields = []
        values = []

        if title is not None:
            fields.append("title = ?")
            values.append(title)
        if description is not None:
            fields.append("description = ?")
            values.append(description)
        if steps is not None:
            fields.append("steps = ?")
            values.append(json.dumps(steps, ensure_ascii=False))
        if category is not None:
            fields.append("category = ?")
            values.append(category)
        if difficulty is not None:
            fields.append("difficulty = ?")
            values.append(difficulty)
        if cook_time_minutes is not None:
            fields.append("cook_time_minutes = ?")
            values.append(cook_time_minutes)
        if is_public is not None:
            fields.append("is_public = ?")
            values.append(int(is_public))
        if cover_image is not None:
            fields.append("cover_image = ?")
            values.append(cover_image)

        if not fields and ingredients is None:
            return False

        try:
            if fields:
                now = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
                fields.append("updated_at = ?")
                values.append(now)
                values.append(recipe_id)
                db.execute(
                    f"UPDATE recipes SET {', '.join(fields)} WHERE id = ?",
                    values,
                )

            if ingredients is not None:
                # 重建食材關聯：先刪除舊的，再寫入新的
                db.execute(
                    "DELETE FROM recipe_ingredients WHERE recipe_id = ?",
                    (recipe_id,),
                )
                cls._save_ingredients(db, recipe_id, ingredients)

            db.commit()
            return True
        except Exception:
            db.rollback()
            return False

    # ------------------------------------------------------------------
    # Delete
    # ------------------------------------------------------------------

    @classmethod
    def delete(cls, recipe_id: int) -> bool:
        """
        刪除指定食譜（CASCADE 會同步移除食材關聯與收藏記錄）。

        Args:
            recipe_id: 食譜 id

        Returns:
            True 表示成功，False 表示失敗。
        """
        db = get_db()
        try:
            db.execute("DELETE FROM recipes WHERE id = ?", (recipe_id,))
            db.commit()
            return True
        except Exception:
            db.rollback()
            return False

    # ------------------------------------------------------------------
    # 私有輔助方法
    # ------------------------------------------------------------------

    @classmethod
    def _save_ingredients(cls, db, recipe_id: int, ingredients: list[dict]):
        """
        寫入食材關聯到 recipe_ingredients 中間表。
        若食材不存在名稱則自動建立。

        Args:
            db:          資料庫連線
            recipe_id:   所屬食譜 id
            ingredients: [{"name": "...", "quantity": "..."}, ...]
        """
        for item in ingredients:
            name = item.get("name", "").strip()
            if not name:
                continue
            ingredient_id = Ingredient.get_or_create(name)
            quantity = item.get("quantity", "")
            db.execute(
                """
                INSERT OR IGNORE INTO recipe_ingredients (recipe_id, ingredient_id, quantity)
                VALUES (?, ?, ?)
                """,
                (recipe_id, ingredient_id, quantity),
            )

    @staticmethod
    def _parse_row(row) -> dict:
        """
        將 sqlite3.Row 轉為 dict，並把 steps JSON 字串還原為 list。
        """
        data = dict(row)
        try:
            data["steps"] = json.loads(data.get("steps", "[]"))
        except (json.JSONDecodeError, TypeError):
            data["steps"] = []
        return data
