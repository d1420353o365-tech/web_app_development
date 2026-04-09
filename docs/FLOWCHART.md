# 流程圖文件 (FLOWCHART) - 食譜收藏夾系統

本文件基於 PRD 與系統架構設計，繪製了使用者的操作流程圖及系統資料處理序列圖。

## 1. 使用者流程圖 (User Flow)

此流程圖展示一般使用者進入系統後，可以執行的主要操作路徑，包含註冊登入、食譜搜尋、食材過濾及個人收藏管理。

```mermaid
flowchart LR
    Start([使用者開啟網頁]) --> Home[首頁 - 瀏覽即將或熱門食譜]
    Home --> Action{選擇操作}
    
    Action -->|註冊 / 登入| Auth[身分驗證頁面]
    Auth -->|成功| Home
    
    Action -->|瀏覽食譜| Browse[食譜列表頁]
    Browse -->|點擊食譜| Detail[單筆食譜詳細頁面]
    
    Detail -->|點擊收藏| SaveAction{是否已登入？}
    SaveAction -->|是| Saved[成功儲存至個人收藏清單]
    SaveAction -->|否| Auth
    
    Action -->|食材搜尋| IngSearch[多重食材組合搜尋頁]
    IngSearch -->|輸入/勾選食材| IngResult[符合食材清單的食譜結果]
    IngResult -->|點擊食譜| Detail
    
    Action -->|新增食譜| AddRecipe[新增食譜表單頁]
    AddRecipe -->|填妥資料並送出| Detail
```

## 2. 系統序列圖 (Sequence Diagram)

此圖以「一般使用者新增並儲存一份食譜」為例，展示完整的前端、後端與資料庫的互動流程。

```mermaid
sequenceDiagram
    actor User as 使用者
    participant Browser as 瀏覽器 (HTML/JS)
    participant Route as Flask Route (Controller)
    participant Model as Recipe Model
    participant DB as SQLite 資料庫

    User->>Browser: 填寫新增食譜表單 (名稱,食材,步驟) 並送出
    Browser->>Route: 發送 POST /recipe/add (附帶表單資料)
    
    Route->>Route: 驗證使用者是否已登入 及 必填欄位
    
    alt 驗證失敗 (未登入或資料缺漏)
        Route-->>Browser: 回傳錯誤提示畫面或重導向至登入頁
    else 驗證成功
        Route->>Model: 建立新的 Recipe 物件並請求儲存
        Model->>DB: 執行 INSERT INTO recipes ... 語法
        DB-->>Model: 回傳操作結果與新生成的 Recipe ID
        
        Model->>DB: 執行 INSERT INTO recipe_ingredients ... 語法寫入關聯食材表
        DB-->>Model: 回傳成功狀態
        
        Model-->>Route: 儲存動作完成
        Route-->>Browser: HTTP 302 重導向到剛新增的食譜詳細頁面
    end
    Browser->>User: 畫面顯示新增成功，以及最新食譜內容
```

## 3. 功能清單對照表

本表列出了 MVP 階段核心功能的 URL 路徑規劃及對應的 HTTP 請求方法，為後續開發階段建立明確標準：

| 功能描述 | URL 路徑 (Route) | HTTP 方法 | 視圖/處理說明 |
| :--- | :--- | :--- | :--- |
| 首頁 (瀏覽推薦食譜) | `/` | GET | 呈現網站首頁 |
| 註冊畫面 | `/auth/register` | GET | 呈現註冊表單 |
| 處理註冊請求 | `/auth/register` | POST | 驗證欄位、雜湊密碼並建立使用者資料 |
| 登入畫面 | `/auth/login` | GET | 呈現登入表單 |
| 處理登入邏輯 | `/auth/login` | POST | 驗證帳戶密碼，通過後建立 Session |
| 登出系統 | `/auth/logout` | GET/POST | 清除現有 Session 並回首頁 |
| 瀏覽/搜尋食譜列表 | `/recipe/` | GET | 支援透過 `?q=關鍵字` 進行名稱搜尋 |
| 食材組合搜尋 | `/recipe/ingredients` | GET | 依據選擇的食材進行複合條件過濾 |
| 新增食譜畫面 | `/recipe/add` | GET | 呈現建立新食譜的輸入表單 (需登入) |
| 處理新增食譜 | `/recipe/add` | POST | 將資料寫入 DB，含多筆食材關聯 |
| 真實食譜內容頁 | `/recipe/<int:id>` | GET | 顯示指定編號的食譜細節 |
| 收藏/取消收藏食譜 | `/recipe/<int:id>/favorite` | POST | 操作收藏關聯資料 |
| 查看我的收藏清單 | `/user/favorites` | GET | 列出該使用者已收藏的所有食譜 |
| 後台管理控制台 | `/admin/` | GET | 顯示全站資料總覽面板 (需管理者權限) |
| 強制刪除違規食譜 | `/admin/recipe/<int:id>/delete`| POST | 管理人員將特定內容自資料庫剔除 |
