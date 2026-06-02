import os
import sqlite3
from flask import Flask, redirect, url_for

def create_app():
    """建立並設定 Flask 應用程式的工廠函數。"""
    app = Flask(__name__, instance_relative_config=True)
    
    # 基本設定 (優先從環境變數載入，無則用開發預設值)
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'dev-secret-key-12345'),
        DATABASE=os.path.join(app.instance_path, 'database.db'),
    )

    # 確保 instance 目錄存在
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # 初始化資料庫
    init_db(app)

    # 註冊 Blueprints (路由模組)
    from app.routes.lottery import lottery_bp
    from app.routes.auth import auth_bp
    from app.routes.record import record_bp
    
    app.register_blueprint(lottery_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(record_bp)

    # 根路由自動重導向至大樂透儀表板 (F-03)
    @app.route('/')
    def root_redirect():
        return redirect(url_for('lottery.dashboard', game_code='lotto'))

    return app

def init_db(app):
    """如果資料庫檔案不存在，則讀取 schema.sql 進行初始化。"""
    db_path = app.config['DATABASE']
    if not os.path.exists(db_path):
        print("⚡ 偵測到資料庫不存在，正在初始化資料庫與預填資料...")
        conn = sqlite3.connect(db_path)
        try:
            # 讀取專案 root 目錄下的 database/schema.sql
            schema_path = os.path.join(app.root_path, '..', 'database', 'schema.sql')
            # 若檔案不存在，試試 app 目錄下的 schema
            if not os.path.exists(schema_path):
                schema_path = os.path.join(app.root_path, 'database', 'schema.sql')
                
            with open(schema_path, 'r', encoding='utf-8') as f:
                conn.executescript(f.read())
            conn.commit()
            print("🎉 資料庫與預填資料初始化成功！")
        except Exception as e:
            print(f"❌ 初始化資料庫失敗: {e}")
        finally:
            conn.close()
