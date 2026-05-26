import sqlite3
from flask import current_app
from werkzeug.security import generate_password_hash, check_password_hash
from app.models.game import get_db_connection

class UserModel:
    @staticmethod
    def create(username, password):
        """建立新使用者帳號。
        
        Args:
            username (str): 使用者名稱
            password (str): 原始密碼
            
        Returns:
            bool: 註冊成功回傳 True，否則回傳 False
        """
        conn = get_db_connection()
        try:
            password_hash = generate_password_hash(password)
            conn.execute(
                'INSERT INTO users (username, password_hash) VALUES (?, ?)',
                (username, password_hash)
            )
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            # 帳號重複 (UNIQUE 限制觸發)
            current_app.logger.warning(f"Registration failed: username '{username}' already exists.")
            return False
        except sqlite3.Error as e:
            current_app.logger.error(f"Database error in UserModel.create: {e}")
            return False
        finally:
            conn.close()

    @staticmethod
    def get_by_username(username):
        """根據使用者名稱查詢使用者。
        
        Args:
            username (str): 使用者名稱
            
        Returns:
            sqlite3.Row: 使用者資料，不存在則回傳 None
        """
        conn = get_db_connection()
        try:
            row = conn.execute(
                'SELECT * FROM users WHERE username = ?',
                (username,)
            ).fetchone()
            return row
        except sqlite3.Error as e:
            current_app.logger.error(f"Database error in UserModel.get_by_username: {e}")
            return None
        finally:
            conn.close()

    @staticmethod
    def get_by_id(user_id):
        """根據 ID 查詢使用者。
        
        Args:
            user_id (int): 使用者 ID
            
        Returns:
            sqlite3.Row: 使用者資料，不存在則回傳 None
        """
        conn = get_db_connection()
        try:
            row = conn.execute(
                'SELECT * FROM users WHERE id = ?',
                (user_id,)
            ).fetchone()
            return row
        except sqlite3.Error as e:
            current_app.logger.error(f"Database error in UserModel.get_by_id: {e}")
            return None
        finally:
            conn.close()

    @staticmethod
    def verify_password(user_row, password):
        """驗證密碼是否正確。
        
        Args:
            user_row (sqlite3.Row): 資料庫中的使用者記錄
            password (str): 使用者輸入的原始密碼
            
        Returns:
            bool: 密碼正確回傳 True，否則回傳 False
        """
        if not user_row:
            return False
        return check_password_hash(user_row['password_hash'], password)
