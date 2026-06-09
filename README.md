# 🎰 運彩與彩券分析統計系統 (Lottery Analytics System)

> 💡 **本專案是一個基於 Python Flask + SQLite + Vanilla CSS & JS 的彩券分析系統。**
>
> 由於 GitHub Pages 僅支援靜態網頁（HTML/CSS/JS），無法直接執行 Python 後端與 SQLite 資料庫，因此本專案**無法使用 GitHub Pages 進行託管**。
>
> 為了讓大家能直接在 GitHub 上「開啟並使用」這個網頁，我們推薦使用免費且支援 Python/Flask 的雲端平台 **Render**，並將部署後的網址連結設定在 GitHub 倉庫的資訊欄中。

---

## 🚀 如何將網頁部署至 Render (免費且自動同步)

Render 提供免費的 Web Service 方案，只要你將程式碼推送到 GitHub，Render 就會自動偵測並重新部署。以下是步驟：

### 第一步：註冊與連結 GitHub
1. 開啟 [Render 官網](https://render.com/)，點擊 **Sign Up**。
2. 建議選擇 **GitHub** 進行註冊與登入，並授權 Render 讀取你的 GitHub 儲存庫。

### 第二步：建立 Web Service
1. 登入後，在 Render Dashboard 點擊 **New +** 按鈕，選擇 **Web Service**。
2. 在儲存庫列表中，找到你的專案 `e04su3su-6`，點擊 **Connect**。

### 第三步：填寫部署設定
在設定頁面中填寫以下欄位（大部分會自動帶入，請確認以下內容）：
- **Name**: `lottery-analytics` (或任何你喜歡的名稱)
- **Region**: 選擇最靠近的區域 (例如 `Singapore` 或 `Oregon`)
- **Branch**: `main`
- **Language**: `Python`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn wsgi:app`
- **Instance Type**: 選擇 **Free** (免費方案)

填寫完成後，滑到最下方點擊 **Create Web Service**。

### 第四步：等待部署完成
- 系統會開始安裝環境並啟動服務，通常需要 2~3 分鐘。
- 當 Log 畫面顯示 `Your service is live!` 時，代表部署成功！
- 頁面最上方會提供一個類似 `https://lottery-analytics.onrender.com` 的專屬網址。

---

## 🔗 在 GitHub 上設定「開啟網頁」連結

部署成功取得網址後，請照以下步驟將網址放到 GitHub 倉庫，讓所有人都能一鍵開啟：

1. 前往你的 GitHub 專案頁面：[https://github.com/alton951129-cloud/e04su3su-6](https://github.com/alton951129-cloud/e04su3su-6)
2. 在頁面右側的 **About** 區塊，點擊齒輪圖標 ⚙️ (Settings)。
3. 在 **Website** 欄位中，貼上你的 Render 部署網址（例如：`https://lottery-analytics.onrender.com`）。
4. 勾選 **Use your GitHub Pages website** 或直接儲存。
5. 這樣專案主頁就會出現 **Website** 連結，大家點擊即可直接開啟網頁使用！

---

## 💻 本地端運行指南 (Local Development)

如果你想在自己的電腦上運行此專案：

### 1. 安裝環境依賴
打開終端機 (Terminal/PowerShell) 並運行：
```bash
pip install -r requirements.txt
```

### 2. 初始化資料庫 (僅需執行一次)
運行資料庫初始化腳本，系統會自動在 `instance/` 資料夾下建立 `database.db` 並填入模擬數據：
```bash
python database.py
```

### 3. 啟動 Flask 開發伺服器
```bash
python app.py
```
啟動後，開啟瀏覽器並輸入 `http://127.0.0.1:5000` 即可訪問網頁。

---

## 📂 專案架構說明

* `app/`：Flask 應用程式核心目錄
  * `models/`：資料庫 Model，負責 SQLite 的 CRUD 操作
  * `routes/`：路由與控制器邏輯 (包含 F-01 到 F-05 各組員負責的區塊)
  * `templates/`：HTML 視圖範本 (Jinja2)
  * `static/`：CSS 樣式表、JS 邏輯及圖片資源
* `database/`：包含 `schema.sql` 初始建表腳本
* `wsgi.py`：Render 部署專用的入口檔案
* `requirements.txt`：專案依賴套件清單 (新增 gunicorn 用於生產環境)
