import sqlite3
import os
import random
from datetime import datetime, timedelta

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'lottery.db')

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. 大樂透 (big_lotto): 6個號碼 (1-49) + 1個特別號 (1-49)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS big_lotto (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            draw_date TEXT NOT NULL,
            draw_number TEXT NOT NULL UNIQUE,
            n1 INTEGER NOT NULL,
            n2 INTEGER NOT NULL,
            n3 INTEGER NOT NULL,
            n4 INTEGER NOT NULL,
            n5 INTEGER NOT NULL,
            n6 INTEGER NOT NULL,
            s_num INTEGER NOT NULL
        )
    ''')

    # 2. 威力彩 (super_lotto): 第一區 6個號碼 (1-38) + 第二區 1個號碼 (1-8)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS super_lotto (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            draw_date TEXT NOT NULL,
            draw_number TEXT NOT NULL UNIQUE,
            n1 INTEGER NOT NULL,
            n2 INTEGER NOT NULL,
            n3 INTEGER NOT NULL,
            n4 INTEGER NOT NULL,
            n5 INTEGER NOT NULL,
            n6 INTEGER NOT NULL,
            s2_num INTEGER NOT NULL
        )
    ''')

    # 3. 今彩539 (daily_cash_539): 5個號碼 (1-39)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS daily_cash_539 (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            draw_date TEXT NOT NULL,
            draw_number TEXT NOT NULL UNIQUE,
            n1 INTEGER NOT NULL,
            n2 INTEGER NOT NULL,
            n3 INTEGER NOT NULL,
            n4 INTEGER NOT NULL,
            n5 INTEGER NOT NULL
        )
    ''')

    conn.commit()

    # 檢查是否需要塞入種子數據 (Seed Data)
    cursor.execute("SELECT COUNT(*) FROM big_lotto")
    if cursor.fetchone()[0] == 0:
        seed_data(conn)

    conn.close()

def seed_data(conn):
    cursor = conn.cursor()
    base_date = datetime.now() - timedelta(days=1)
    
    # --- 1. 大樂透 (每週二、五開獎) ---
    big_lotto_records = []
    current_date = base_date
    draw_count = 1
    # 產生 50 期
    while len(big_lotto_records) < 50:
        # 尋找週二 (1) 或週五 (4)
        if current_date.weekday() in (1, 4):
            date_str = current_date.strftime('%Y-%m-%d')
            draw_num = f"115000{50 - len(big_lotto_records):02d}"
            # 隨機產生不重複的 6 個號碼 (1-49)，排序
            nums = sorted(random.sample(range(1, 50), 6))
            # 特別號 (1-49)，且不能與前 6 個重複
            available_special = [n for n in range(1, 50) if n not in nums]
            special = random.choice(available_special)
            big_lotto_records.append((date_str, draw_num, nums[0], nums[1], nums[2], nums[3], nums[4], nums[5], special))
        current_date -= timedelta(days=1)
    
    # 插入大樂透 (反轉陣列讓舊期數在前面，id 就會順序遞增)
    cursor.executemany('''
        INSERT OR IGNORE INTO big_lotto (draw_date, draw_number, n1, n2, n3, n4, n5, n6, s_num)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', reversed(big_lotto_records))


    # --- 2. 威力彩 (每週一、四開獎) ---
    super_lotto_records = []
    current_date = base_date
    while len(super_lotto_records) < 50:
        # 尋找週一 (0) 或週四 (3)
        if current_date.weekday() in (0, 3):
            date_str = current_date.strftime('%Y-%m-%d')
            draw_num = f"115000{50 - len(super_lotto_records):02d}"
            # 第一區隨機 6 個號碼 (1-38)
            nums = sorted(random.sample(range(1, 39), 6))
            # 第二區隨機 1 個號碼 (1-8)
            sec2 = random.randint(1, 8)
            super_lotto_records.append((date_str, draw_num, nums[0], nums[1], nums[2], nums[3], nums[4], nums[5], sec2))
        current_date -= timedelta(days=1)
        
    cursor.executemany('''
        INSERT OR IGNORE INTO super_lotto (draw_date, draw_number, n1, n2, n3, n4, n5, n6, s2_num)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', reversed(super_lotto_records))


    # --- 3. 今彩539 (每週一至週六開獎，週日不開) ---
    daily_cash_records = []
    current_date = base_date
    while len(daily_cash_records) < 50:
        # 週日是 6 (Weekday index)
        if current_date.weekday() != 6:
            date_str = current_date.strftime('%Y-%m-%d')
            draw_num = f"115000{50 - len(daily_cash_records):02d}"
            # 隨機 5 個號碼 (1-39)
            nums = sorted(random.sample(range(1, 40), 5))
            daily_cash_records.append((date_str, draw_num, nums[0], nums[1], nums[2], nums[3], nums[4]))
        current_date -= timedelta(days=1)

    cursor.executemany('''
        INSERT OR IGNORE INTO daily_cash_539 (draw_date, draw_number, n1, n2, n3, n4, n5)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', reversed(daily_cash_records))

    conn.commit()

if __name__ == '__main__':
    init_db()
    print("Database initialized successfully with mock history data.")
