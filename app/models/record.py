import sqlite3
from flask import current_app
from app.models.game import get_db_connection

class RecordModel:
    @staticmethod
    def create(user_id, game_code, cost, prize, record_date):
        """新增一筆投注盈虧紀錄。
        
        Args:
            user_id (int): 使用者 ID
            game_code (str): 彩券代碼 (如 'lotto')
            cost (int): 投注成本金額
            prize (int): 中獎金額
            record_date (str): 投注日期 (格式: YYYY-MM-DD)
            
        Returns:
            bool: 新增成功回傳 True，否則回傳 False
        """
        conn = get_db_connection()
        try:
            conn.execute(
                'INSERT INTO records (user_id, game_code, cost, prize, record_date) '
                'VALUES (?, ?, ?, ?, ?)',
                (user_id, game_code, cost, prize, record_date)
            )
            conn.commit()
            return True
        except sqlite3.Error as e:
            current_app.logger.error(f"Database error in RecordModel.create: {e}")
            return False
        finally:
            conn.close()

    @staticmethod
    def get_by_user(user_id):
        """查詢某使用者的所有投注紀錄（包含彩券中文名稱）。
        
        Args:
            user_id (int): 使用者 ID
            
        Returns:
            list[sqlite3.Row]: 投注記錄清單
        """
        conn = get_db_connection()
        try:
            rows = conn.execute(
                'SELECT r.*, g.name as game_name '
                'FROM records r '
                'JOIN games g ON r.game_code = g.game_code '
                'WHERE r.user_id = ? '
                'ORDER BY r.record_date DESC, r.id DESC',
                (user_id,)
            ).fetchall()
            return rows
        except sqlite3.Error as e:
            current_app.logger.error(f"Database error in RecordModel.get_by_user: {e}")
            return []
        finally:
            conn.close()

    @staticmethod
    def delete(record_id, user_id):
        """安全刪除某使用者的特定投注紀錄（防止越權）。
        
        Args:
            record_id (int): 紀錄 ID
            user_id (int): 使用者 ID
            
        Returns:
            bool: 刪除成功回傳 True，否則回傳 False
        """
        conn = get_db_connection()
        try:
            cursor = conn.execute(
                'DELETE FROM records WHERE id = ? AND user_id = ?',
                (record_id, user_id)
            )
            conn.commit()
            # 判斷是否有實際影響行數 (防刪除不存在或不屬於該用戶的記錄)
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            current_app.logger.error(f"Database error in RecordModel.delete: {e}")
            return False
        finally:
            conn.close()

    @staticmethod
    def get_stats_by_user(user_id):
        """統計某使用者的總花費、總中獎、淨損益與投資報酬率 (ROI)。
        
        Args:
            user_id (int): 使用者 ID
            
        Returns:
            dict: 統計數據字典，包含 cost, prize, net, roi
        """
        conn = get_db_connection()
        try:
            row = conn.execute(
                'SELECT SUM(cost) as total_cost, SUM(prize) as total_prize '
                'FROM records WHERE user_id = ?',
                (user_id,)
            ).fetchone()
            
            total_cost = row['total_cost'] if row['total_cost'] is not None else 0
            total_prize = row['total_prize'] if row['total_prize'] is not None else 0
            net = total_prize - total_cost
            roi = (total_prize / total_cost * 100) if total_cost > 0 else 0.0
            
            return {
                'cost': total_cost,
                'prize': total_prize,
                'net': net,
                'roi': roi
            }
        except sqlite3.Error as e:
            current_app.logger.error(f"Database error in RecordModel.get_stats_by_user: {e}")
            return {'cost': 0, 'prize': 0, 'net': 0, 'roi': 0.0}
        finally:
            conn.close()
