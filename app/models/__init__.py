"""
app/models/__init__.py
匯出所有 Model，方便其他模組統一 import。
"""

from .database import get_db, init_db
from .user import User
from .recipe import Recipe
from .ingredient import Ingredient
from .favorite import Favorite

__all__ = [
    "get_db",
    "init_db",
    "User",
    "Recipe",
    "Ingredient",
    "Favorite",
]
