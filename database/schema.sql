-- =============================================================
-- 食譜收藏夾系統 - SQLite 資料庫建表語法
-- 檔案: database/schema.sql
-- 說明: 請在專案根目錄執行以下指令以初始化資料庫：
--       sqlite3 instance/database.db < database/schema.sql
-- =============================================================

PRAGMA foreign_keys = ON;

-- -------------------------------------------------------------
-- 資料表 1: users（使用者）
-- -------------------------------------------------------------
CREATE TABLE IF NOT EXISTS users (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    username        TEXT    NOT NULL UNIQUE,
    email           TEXT    NOT NULL UNIQUE,
    password_hash   TEXT    NOT NULL,
    is_admin        INTEGER NOT NULL DEFAULT 0,   -- 0: 一般使用者, 1: 管理員
    created_at      TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%S', 'now', 'localtime'))
);

CREATE INDEX IF NOT EXISTS idx_users_email    ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);

-- -------------------------------------------------------------
-- 資料表 2: recipes（食譜）
-- -------------------------------------------------------------
CREATE TABLE IF NOT EXISTS recipes (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id             INTEGER NOT NULL,
    title               TEXT    NOT NULL,
    description         TEXT,
    steps               TEXT    NOT NULL,          -- JSON 陣列字串，例如: ["步驟一", "步驟二"]
    category            TEXT,                      -- 例如: 家常 / 甜點 / 健身
    difficulty          TEXT,                      -- 值域: easy / medium / hard
    cook_time_minutes   INTEGER,
    is_public           INTEGER NOT NULL DEFAULT 1, -- 1: 公開, 0: 私人
    cover_image         TEXT,
    created_at          TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%S', 'now', 'localtime')),
    updated_at          TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%S', 'now', 'localtime')),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_recipes_user_id   ON recipes(user_id);
CREATE INDEX IF NOT EXISTS idx_recipes_is_public ON recipes(is_public);
CREATE INDEX IF NOT EXISTS idx_recipes_category  ON recipes(category);
CREATE INDEX IF NOT EXISTS idx_recipes_title     ON recipes(title);

-- -------------------------------------------------------------
-- 資料表 3: ingredients（食材）
-- -------------------------------------------------------------
CREATE TABLE IF NOT EXISTS ingredients (
    id      INTEGER PRIMARY KEY AUTOINCREMENT,
    name    TEXT    NOT NULL UNIQUE               -- 食材名稱全站唯一
);

CREATE INDEX IF NOT EXISTS idx_ingredients_name ON ingredients(name);

-- -------------------------------------------------------------
-- 資料表 4: recipe_ingredients（食譜-食材 多對多中間表）
-- -------------------------------------------------------------
CREATE TABLE IF NOT EXISTS recipe_ingredients (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    recipe_id       INTEGER NOT NULL,
    ingredient_id   INTEGER NOT NULL,
    quantity        TEXT,                          -- 用量描述，如: 2顆 / 100g
    UNIQUE (recipe_id, ingredient_id),             -- 同一食譜不重複加同一食材
    FOREIGN KEY (recipe_id)     REFERENCES recipes(id)     ON DELETE CASCADE,
    FOREIGN KEY (ingredient_id) REFERENCES ingredients(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_ri_recipe_id     ON recipe_ingredients(recipe_id);
CREATE INDEX IF NOT EXISTS idx_ri_ingredient_id ON recipe_ingredients(ingredient_id);

-- -------------------------------------------------------------
-- 資料表 5: favorites（使用者收藏）
-- -------------------------------------------------------------
CREATE TABLE IF NOT EXISTS favorites (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     INTEGER NOT NULL,
    recipe_id   INTEGER NOT NULL,
    created_at  TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%S', 'now', 'localtime')),
    UNIQUE (user_id, recipe_id),                   -- 一位使用者對一個食譜只能收藏一次
    FOREIGN KEY (user_id)   REFERENCES users(id)   ON DELETE CASCADE,
    FOREIGN KEY (recipe_id) REFERENCES recipes(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_favorites_user_id   ON favorites(user_id);
CREATE INDEX IF NOT EXISTS idx_favorites_recipe_id ON favorites(recipe_id);
