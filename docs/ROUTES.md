# 路由設計文件 (ROUTES) - 食譜收藏夾系統

本文件根據 PRD.md、ARCHITECTURE.md、FLOWCHART.md 與 DB_DESIGN.md，定義系統所有頁面的路由規劃、輸入輸出與模板對應。

---

## 1. 路由總覽表格

### 🔐 身分驗證（Blueprint: `auth`，前綴 `/auth`）

| 功能 | HTTP 方法 | URL 路徑 | 對應模板 | 說明 |
| :--- | :---: | :--- | :--- | :--- |
| 登入頁面 | GET | `/auth/login` | `auth/login.html` | 顯示登入表單 |
| 處理登入 | POST | `/auth/login` | — | 驗證帳密，建立 Session，重導向首頁 |
| 註冊頁面 | GET | `/auth/register` | `auth/register.html` | 顯示註冊表單 |
| 處理註冊 | POST | `/auth/register` | — | 驗證欄位、hash 密碼，建立帳號，重導向登入 |
| 登出 | POST | `/auth/logout` | — | 清除 Session，重導向首頁 |

### 🍳 食譜（Blueprint: `recipe`，前綴 `/recipe`）

| 功能 | HTTP 方法 | URL 路徑 | 對應模板 | 說明 |
| :--- | :---: | :--- | :--- | :--- |
| 首頁 / 瀏覽食譜 | GET | `/` | `recipe/index.html` | 顯示公開食譜列表，支援 `?q=` 關鍵字搜尋 |
| 食材組合搜尋頁 | GET | `/recipe/search` | `recipe/search.html` | 顯示食材勾選介面與搜尋結果 |
| 新增食譜頁面 | GET | `/recipe/add` | `recipe/form.html` | 顯示新增食譜表單（需登入） |
| 處理新增食譜 | POST | `/recipe/add` | — | 寫入食譜與食材關聯，重導向詳細頁 |
| 食譜詳細頁面 | GET | `/recipe/<int:id>` | `recipe/detail.html` | 顯示單筆食譜完整內容 |
| 編輯食譜頁面 | GET | `/recipe/<int:id>/edit` | `recipe/form.html` | 顯示預填資料的編輯表單（需登入、需為作者） |
| 處理編輯食譜 | POST | `/recipe/<int:id>/edit` | — | 更新食譜資料，重導向詳細頁 |
| 刪除食譜 | POST | `/recipe/<int:id>/delete` | — | 刪除食譜，重導向首頁 |
| 收藏 / 取消收藏 | POST | `/recipe/<int:id>/favorite` | — | 切換收藏狀態，回傳 JSON 結果 |

### 👤 使用者（Blueprint: `user`，前綴 `/user`）

| 功能 | HTTP 方法 | URL 路徑 | 對應模板 | 說明 |
| :--- | :---: | :--- | :--- | :--- |
| 我的收藏清單 | GET | `/user/favorites` | `user/favorites.html` | 顯示登入使用者的所有收藏食譜（需登入） |

### 🛡️ 後台管理（Blueprint: `admin`，前綴 `/admin`）

| 功能 | HTTP 方法 | URL 路徑 | 對應模板 | 說明 |
| :--- | :---: | :--- | :--- | :--- |
| 管理後台首頁 | GET | `/admin/` | `admin/dashboard.html` | 全站資料總覽：使用者數、食譜數（需管理員） |
| 使用者列表 | GET | `/admin/users` | `admin/users.html` | 列出所有使用者（需管理員） |
| 刪除使用者 | POST | `/admin/users/<int:id>/delete` | — | 強制刪除使用者帳號（需管理員） |
| 食譜管理列表 | GET | `/admin/recipes` | `admin/recipes.html` | 列出所有食譜，含公開/私人狀態（需管理員） |
| 強制刪除食譜 | POST | `/admin/recipe/<int:id>/delete` | — | 管理員刪除違規食譜（需管理員） |

---

## 2. 每個路由的詳細說明

---

### 🔐 Auth Blueprint

#### `GET /auth/login` — 登入頁面
- **輸入**: 無
- **處理邏輯**: 若使用者已登入（Session 存在 `user_id`），直接重導向首頁
- **輸出**: 渲染 `auth/login.html`，傳入空白表單
- **錯誤處理**: 無

#### `POST /auth/login` — 處理登入
- **輸入（表單）**: `email`, `password`
- **處理邏輯**:
  1. 驗證欄位不為空
  2. `User.get_by_email(email)` 查詢使用者
  3. `User.verify_password(hash, password)` 驗證密碼
  4. 通過後將 `user_id` 與 `is_admin` 存入 `session`
- **輸出**: 重導向至 `/`（首頁）
- **錯誤處理**: 帳密錯誤 → `flash("帳號或密碼錯誤")` → 重新渲染登入表單

#### `GET /auth/register` — 註冊頁面
- **輸入**: 無
- **處理邏輯**: 若已登入則重導向首頁
- **輸出**: 渲染 `auth/register.html`

#### `POST /auth/register` — 處理註冊
- **輸入（表單）**: `username`, `email`, `password`, `password_confirm`
- **處理邏輯**:
  1. 驗證所有欄位不為空
  2. 驗證 `password == password_confirm`
  3. `User.get_by_email(email)` 檢查 email 是否已被註冊
  4. `User.create(username, email, password)` 建立帳號
- **輸出**: 重導向 `/auth/login`，附帶 flash 成功訊息
- **錯誤處理**: 欄位缺漏 / email 重複 / 密碼不一致 → `flash(錯誤訊息)` → 重新渲染表單

#### `POST /auth/logout` — 登出
- **輸入**: 無
- **處理邏輯**: `session.clear()` 清除 Session
- **輸出**: 重導向至 `/`（首頁）
- **錯誤處理**: 無

---

### 🍳 Recipe Blueprint

#### `GET /` — 首頁 / 食譜列表
- **輸入（Query String）**: `?q=關鍵字`（可選）
- **處理邏輯**:
  - 若有 `q` 參數：`Recipe.search_by_keyword(q)`
  - 若無：`Recipe.get_all(public_only=True)`
- **輸出**: 渲染 `recipe/index.html`，傳入 `recipes` list、`query` 字串
- **錯誤處理**: 無

#### `GET /recipe/search` — 食材組合搜尋頁
- **輸入（Query String）**: `?ingredients=雞蛋&ingredients=番茄`（可多選）
- **處理邏輯**:
  1. `Ingredient.get_all()` 取得所有食材供勾選
  2. 若有送出食材：`Recipe.search_by_ingredients(ingredient_names)`
- **輸出**: 渲染 `recipe/search.html`，傳入 `all_ingredients`、`results`、`selected`
- **錯誤處理**: 未選食材時顯示提示訊息

#### `GET /recipe/add` — 新增食譜頁面（需登入）
- **輸入**: 無
- **處理邏輯**: 檢查 Session 確認已登入，取得 `Ingredient.get_all()` 供食材自動完成
- **輸出**: 渲染 `recipe/form.html`，傳入空白 `recipe` dict、`all_ingredients`
- **錯誤處理**: 未登入 → 重導向 `/auth/login`

#### `POST /recipe/add` — 處理新增食譜（需登入）
- **輸入（表單）**: `title`, `description`, `steps[]`, `category`, `difficulty`, `cook_time_minutes`, `is_public`, `ingredient_name[]`, `ingredient_quantity[]`
- **處理邏輯**:
  1. 確認已登入
  2. 驗證 `title` 與 `steps` 不為空
  3. 組合 `ingredients` list（`[{"name":..., "quantity":...}]`）
  4. `Recipe.create(user_id, title, steps, ..., ingredients)` 儲存
- **輸出**: 重導向至 `/recipe/<new_id>`
- **錯誤處理**: 欄位缺漏 → `flash(錯誤)` → 重新渲染表單

#### `GET /recipe/<int:id>` — 食譜詳細頁面
- **輸入（URL）**: `id`（食譜 id）
- **處理邏輯**:
  1. `Recipe.get_by_id(id)` 取得食譜（含食材、步驟）
  2. 若使用者已登入：`Favorite.is_favorited(user_id, id)` 取得收藏狀態
  3. `Favorite.get_count_by_recipe(id)` 取得收藏人數
- **輸出**: 渲染 `recipe/detail.html`，傳入 `recipe`、`is_favorited`、`fav_count`
- **錯誤處理**: 食譜不存在 → `abort(404)`；私人食譜且非作者 → `abort(403)`

#### `GET /recipe/<int:id>/edit` — 編輯食譜頁面（需登入、需為作者）
- **輸入（URL）**: `id`
- **處理邏輯**:
  1. `Recipe.get_by_id(id)` 取得食譜
  2. 確認 `recipe["user_id"] == session["user_id"]` 或 `is_admin`
  3. `Ingredient.get_all()` 取得全部食材
- **輸出**: 渲染 `recipe/form.html`，傳入預填的 `recipe`、`all_ingredients`（`is_edit=True`）
- **錯誤處理**: 未登入 → 重導向登入；非作者 → `abort(403)`；不存在 → `abort(404)`

#### `POST /recipe/<int:id>/edit` — 處理編輯食譜（需登入、需為作者）
- **輸入（表單）**: 同新增表單欄位
- **處理邏輯**:
  1. 確認作者身份
  2. `Recipe.update(id, ...)` 更新資料
- **輸出**: 重導向至 `/recipe/<id>`
- **錯誤處理**: 驗證失敗 → `flash(錯誤)` → 重新渲染編輯表單

#### `POST /recipe/<int:id>/delete` — 刪除食譜（需登入、需為作者或管理員）
- **輸入（URL）**: `id`
- **處理邏輯**:
  1. 確認使用者身份（作者或管理員）
  2. `Recipe.delete(id)` 刪除
- **輸出**: 重導向至 `/`（首頁）
- **錯誤處理**: 無權限 → `abort(403)`；不存在 → `abort(404)`

#### `POST /recipe/<int:id>/favorite` — 收藏切換（需登入）
- **輸入（URL）**: `id`
- **處理邏輯**:
  1. 確認已登入
  2. `Favorite.toggle(user_id, recipe_id)` 切換收藏狀態
- **輸出**: 回傳 JSON `{"status": "added" | "removed"}`（供前端 JS 更新按鈕狀態）
- **錯誤處理**: 未登入 → 回傳 JSON `{"error": "請先登入", "redirect": "/auth/login"}`

---

### 👤 User Blueprint

#### `GET /user/favorites` — 我的收藏清單（需登入）
- **輸入**: 無
- **處理邏輯**: `Favorite.get_by_user(session["user_id"])` 取得收藏食譜列表
- **輸出**: 渲染 `user/favorites.html`，傳入 `favorites` list
- **錯誤處理**: 未登入 → 重導向 `/auth/login`

---

### 🛡️ Admin Blueprint

#### `GET /admin/` — 管理後台首頁（需管理員）
- **輸入**: 無
- **處理邏輯**: 彙整 `User.get_all()`、`Recipe.get_all()` 等統計資料
- **輸出**: 渲染 `admin/dashboard.html`，傳入 `user_count`、`recipe_count`、`recent_recipes`
- **錯誤處理**: 非管理員 → `abort(403)`

#### `GET /admin/users` — 使用者列表（需管理員）
- **輸入**: 無
- **處理邏輯**: `User.get_all()` 取得所有使用者
- **輸出**: 渲染 `admin/users.html`，傳入 `users` list
- **錯誤處理**: 非管理員 → `abort(403)`

#### `POST /admin/users/<int:id>/delete` — 刪除使用者（需管理員）
- **輸入（URL）**: `id`
- **處理邏輯**: `User.delete(id)` 刪除（CASCADE 同步刪除其食譜與收藏）
- **輸出**: 重導向 `/admin/users`，附帶 flash 訊息
- **錯誤處理**: 不存在 → `abort(404)`

#### `GET /admin/recipes` — 食譜管理列表（需管理員）
- **輸入**: 無
- **處理邏輯**: `Recipe.get_all(public_only=False)` 取得全站食譜（含私人）
- **輸出**: 渲染 `admin/recipes.html`，傳入 `recipes` list
- **錯誤處理**: 非管理員 → `abort(403)`

#### `POST /admin/recipe/<int:id>/delete` — 強制刪除食譜（需管理員）
- **輸入（URL）**: `id`
- **處理邏輯**: `Recipe.delete(id)` 刪除
- **輸出**: 重導向 `/admin/recipes`，附帶 flash 訊息
- **錯誤處理**: 不存在 → `abort(404)`

---

## 3. Jinja2 模板清單

所有模板繼承自 `base.html`（`{% extends "base.html" %}`）。

| 模板路徑 | 繼承自 | 說明 |
| :--- | :--- | :--- |
| `base.html` | — | 全站共用 Layout（Navbar、Flash 訊息、Footer） |
| `auth/login.html` | `base.html` | 登入表單（email + password） |
| `auth/register.html` | `base.html` | 註冊表單（username + email + password x2） |
| `recipe/index.html` | `base.html` | 首頁食譜卡片列表、關鍵字搜尋列 |
| `recipe/search.html` | `base.html` | 食材勾選介面 + 搜尋結果列表 |
| `recipe/form.html` | `base.html` | 新增 / 編輯食譜通用表單（`is_edit` 旗標切換） |
| `recipe/detail.html` | `base.html` | 食譜詳細頁（食材、步驟、收藏按鈕） |
| `user/favorites.html` | `base.html` | 使用者收藏清單（食譜卡片列表） |
| `admin/dashboard.html` | `base.html` | 管理後台總覽面板（統計數字、快捷連結） |
| `admin/users.html` | `base.html` | 使用者管理列表（含刪除按鈕） |
| `admin/recipes.html` | `base.html` | 全站食譜管理列表（含強制刪除按鈕） |
| `errors/404.html` | `base.html` | 找不到頁面錯誤畫面 |
| `errors/403.html` | `base.html` | 無存取權限錯誤畫面 |
