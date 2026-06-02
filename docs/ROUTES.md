# Flask 路由與 API 設計 (Flask Routes & API Design)

> **專案名稱**：運彩分析系統 (Sports Lottery Analysis System)  
> **對應 SDLC 階段**：路由與介面規劃 (Routing & Interface Planning)  
> **日期**：2026-05-26  

---

## 1. 全系統路由對照總覽表

本系統分為 `lottery`、`stats`、`auth`、`record` 等四大模組，其 Flask 路由規劃如下：

| 功能名稱 | HTTP 方法 | URL 路由路徑 | 對應 Jinja2 模板 | 認證要求 | 負責人 | 說明 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **首頁跳轉** | GET | `/` | — | 訪客/會員 | 全組 | 預設重導向至 `/lottery/lotto` |
| **F-03 彩券大盤**| GET | `/lottery/<game_code>` | `lottery/dashboard.html` | 訪客/會員 | **蔡宗孟**| 切換不同彩券看板並展示數據與預測 |
| **F-01 頻率數據**| GET | `/lottery/<game_code>/stats`| — (JSON) | 訪客/會員 | **黃彥閎**| 返回號碼開出次數的 JSON 統計 API |
| **F-02 生成號碼**| POST | `/lottery/<game_code>/generate`| — (重導向) | 訪客/會員 | **廖銘麒**| 提交參數，生成最有可能的號碼組合 |
| **F-05 註冊頁面**| GET | `/register` | `auth/register.html` | 僅限訪客 | **李軒睿**| 展示使用者註冊表單 |
| **F-05 註冊提交**| POST | `/register` | — (重導向) | 僅限訪客 | **李軒睿**| 處理密碼加密並建立帳號 |
| **F-05 登入頁面**| GET | `/login` | `auth/login.html` | 僅限訪客 | **李軒睿**| 展示使用者登入表單 |
| **F-05 登入提交**| POST | `/login` | — (重導向) | 僅限訪客 | **李軒睿**| 驗證帳號密碼並建立會話 |
| **F-05 使用者登出**| GET | `/logout` | — (重導向) | 僅限會員 | **李軒睿**| 清除會話並重導回登入頁面 |
| **F-04 記帳清單**| GET | `/records` | `lottery/records.html` | 僅限會員 | **黃昰傑**| 顯示個人投注記錄列表與記帳儀表板 |
| **F-04 新增記帳**| POST | `/records/add` | — (重導向) | 僅限會員 | **黃昰傑**| 接收記帳表單，防越權存入資料庫 |
| **F-04 刪除記帳**| POST | `/records/<int:id>/delete`| — (重導向)| 僅限會員 | **黃昰傑**| 接收 POST 請求，刪除指定記帳記錄 |

---

## 2. 核心路由詳細規格設計

### 2.1 F-03 彩券大盤路由 (由蔡宗孟負責)
* **URL 路徑**：`/lottery/<game_code>`
* **HTTP 方法**：`GET`
* **路由變數**：`game_code`（如 `'lotto'`, `'mark_six'`, `'daily_cash_539'`）
* **輸入參數**：無
* **業務邏輯**：
  1. 呼叫 `GameModel.get_by_code(game_code)` 獲取彩券規則，若不存在則回傳 404。
  2. 呼叫 F-01 提供之 `HistoryModel.get_recent_draws(game_code, limit=10)` 查詢最近 10 期開獎號碼。
  3. 呼叫 F-01 提供之 `HistoryModel.get_number_frequency(game_code)` 計算號碼出現次數。
  4. 從 `session` 檢查用戶是否登入。若已登入，可選擇預填記帳的彩券種類。
  5. 調用 `render_template('lottery/dashboard.html')` 進行頁面渲染。
* **錯誤處理**：
  * 若 `game_code` 在 `games` 表中找不到，回傳 `flask.abort(404)`。

### 2.2 F-04 新增記帳記錄路由 (由黃昰傑負責)
* **URL 路徑**：`/records/add`
* **HTTP 方法**：`POST`
* **認證防護**：需驗證 `session.get('user_id')` 是否存在。未登入者拒絕存取並重導至 `/login`。
* **輸入參數 (表單欄位)**：
  * `game_code` (str): 彩券代碼，必填，如 `'lotto'`。
  * `cost` (int): 投注花費，必填且必須大於 0。
  * `prize` (int): 中獎金額，必填且必須大於或等於 0。
  * `record_date` (str): 投注日期，格式為 YYYY-MM-DD，必填。
* **業務邏輯**：
  1. 從會話取得 `user_id`。
  2. 驗證欄位是否為空。若驗證失敗，呼叫 `flash("請填寫所有欄位")` 並重導向回 `/records`。
  3. 驗證 `cost` 與 `prize` 數值。若小於 0，呼叫 `flash("金額不能為負數")` 並重導向。
  4. 呼叫 `RecordModel.create(user_id, game_code, cost, prize, record_date)` 將資料寫入 SQLite。
  5. 寫入成功後，呼叫 `flash("投注記錄已成功新增", "success")` 並重導向至 `/records`。
* **錯誤處理**：
  * 若資料庫寫入拋出異常，記錄日誌並回傳 `flash("系統繁忙，請稍後再試", "danger")`。

---

## 3. Jinja2 HTML 模板對照清單

系統中所有視圖模板檔案均存放在 `app/templates/` 下：

1. **`base.html`** (基礎模板骨架)
   * *功能*：定義全系統的 `<head>`、引進 Bootstrap 5 CDN 與自訂義 `style.css`。實作全局的暗黑毛玻璃導覽列、登入狀態顯示，以及 flash 訊息的全局渲染區塊。
2. **`auth/login.html`** (登入頁)
   * *功能*：繼承 `base.html`，提供精美的毛玻璃登入卡片，包含帳號、密碼輸入欄與註冊跳轉連結。
3. **`auth/register.html`** (註冊頁)
   * *功能*：繼承 `base.html`，提供毛玻璃註冊卡片。
4. **`lottery/dashboard.html`** (彩券核心儀表板大盤)
   * *功能*：繼承 `base.html`。
     * 頂部渲染 **F-03 彩券種類切換卡片**（大樂透、六合彩、今彩539）。
     * 左下方顯示 F-01 最近 10 期歷史開獎數字。
     * 中間顯示 F-01 的冷熱門數字統計與分析。
     * 右下方顯示 F-02 的預測推薦號碼生成按鈕與結果展示。
5. **`lottery/records.html`** (個人記帳儀表板)
   * *功能*：繼承 `base.html`。
     * 頂部顯示個人財務總分析（總花費、總中獎、淨盈虧及投資報酬率，伴隨紅/綠雙色動態顯示）。
     * 左側提供「新增投注記錄」精美表單（自動預填當前彩券代碼）。
     * 右側以表格展示歷史記帳紀錄，並為每條記錄提供「刪除」按鈕。

---

*本路由設計文件為 `app/routes/` 核心路由邏輯與 `app/templates/` Jinja2 模板對接開發的最高綱領。*
