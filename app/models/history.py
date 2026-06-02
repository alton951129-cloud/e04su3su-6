import sqlite3
from collections import Counter
from flask import current_app
from app.models.game import get_db_connection

class HistoryModel:
    @staticmethod
    def get_recent_draws(game_code, limit=10):
        """獲取某種彩券最近的開獎記錄。
        
        Args:
            game_code (str): 彩券代碼 (如 'lotto')
            limit (int): 查詢筆數限制
            
        Returns:
            list[sqlite3.Row]: 開獎紀錄列表
        """
        conn = get_db_connection()
        try:
            rows = conn.execute(
                'SELECT * FROM lottery_history WHERE game_code = ? '
                'ORDER BY draw_date DESC, draw_period DESC LIMIT ?',
                (game_code, limit)
            ).fetchall()
            return rows
        except sqlite3.Error as e:
            current_app.logger.error(f"Database error in HistoryModel.get_recent_draws: {e}")
            return []
        finally:
            conn.close()

    @staticmethod
    def get_number_frequency(game_code):
        """分析某種彩券的號碼開出頻率，並得出冷熱門號碼。
        
        Args:
            game_code (str): 彩券代碼
            
        Returns:
            dict: 包含所有號碼頻率、前 5 熱門號碼、前 5 冷門號碼的字典
        """
        conn = get_db_connection()
        try:
            # 1. 取得彩券規格限制 (以得知總球數範圍)
            game = conn.execute(
                'SELECT max_number FROM games WHERE game_code = ?', (game_code,)
            ).fetchone()
            
            if not game:
                return {'frequency': {}, 'hot': [], 'cold': []}
                
            max_num = game['max_number']
            
            # 2. 獲取所有歷史開獎紀錄的普通中獎號碼
            rows = conn.execute(
                'SELECT winning_numbers FROM lottery_history WHERE game_code = ?',
                (game_code,)
            ).fetchall()
            
            # 3. 統計每個號碼出現的次數
            counter = Counter()
            for row in rows:
                # 歷史號碼是以逗號分隔的字串，例如 "08,12,19,25,32,44"
                numbers = [int(x.strip()) for x in row['winning_numbers'].split(',') if x.strip()]
                counter.update(numbers)
            
            # 確保所有可能出現的號碼都在統計中 (即使次數為 0)
            full_freq = {}
            for num in range(1, max_num + 1):
                full_freq[num] = counter.get(num, 0)
            
            # 4. 排序得出冷熱門號碼
            sorted_freq = sorted(full_freq.items(), key=lambda item: item[1], reverse=True)
            
            hot_numbers = [num for num, count in sorted_freq[:5]]
            cold_numbers = [num for num, count in sorted_freq[-5:]][::-1] # 顛倒以讓最冷門的排前面
            
            return {
                'frequency': full_freq,      # {1: 3, 2: 0, 3: 5, ...}
                'hot': hot_numbers,          # [15, 23, 8, ...]
                'cold': cold_numbers         # [2, 49, 12, ...]
            }
        except sqlite3.Error as e:
            current_app.logger.error(f"Database error in HistoryModel.get_number_frequency: {e}")
            return {'frequency': {}, 'hot': [], 'cold': []}
        finally:
            conn.close()
