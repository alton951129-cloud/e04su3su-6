import sqlite3
import os
from flask import current_app

def get_db_connection():
    """取得資料庫連線，設定以 Row 方式取值並啟用外鍵約束。"""
    # 優先從 Flask 的 config 讀取資料庫路徑，若無則預設為 instance/database.db
    db_path = current_app.config['DATABASE']
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

class GameModel:
    @staticmethod
    def get_by_code(game_code):
        """根據英文代碼獲取彩券種類。
        
        Args:
            game_code (str): 彩券識別代碼 (如 'lotto')
            
        Returns:
            sqlite3.Row: 若存在則回傳 Row 物件，否則回傳 None
        """
        conn = get_db_connection()
        try:
            row = conn.execute(
                'SELECT * FROM games WHERE game_code = ?', (game_code,)
            ).fetchone()
            return row
        except sqlite3.Error as e:
            current_app.logger.error(f"Database error in GameModel.get_by_code: {e}")
            return None
        finally:
            conn.close()

    @staticmethod
    def get_all():
        """獲取系統中支援的所有彩券種類。
        
        Returns:
            list[sqlite3.Row]: 彩券種類清單
        """
        conn = get_db_connection()
        try:
            rows = conn.execute('SELECT * FROM games ORDER BY id ASC').fetchall()
            return rows
        except sqlite3.Error as e:
            current_app.logger.error(f"Database error in GameModel.get_all: {e}")
            return []
        finally:
            conn.close()
