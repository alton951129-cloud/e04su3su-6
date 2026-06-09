import os
import sqlite3
import requests
import json
from TaiwanLottery import TaiwanLotteryCrawler

def get_db_path():
    """Dynamically get the database path, supporting both Flask route and command line contexts."""
    try:
        from flask import current_app
        return current_app.config['DATABASE']
    except RuntimeError:
        # Outside Flask application context
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'instance', 'database.db')

def sync_lotto(conn):
    """Sync Taiwan Lotto 6/49 (大樂透) data."""
    crawler = TaiwanLotteryCrawler()
    try:
        results = crawler.lotto649()
    except Exception as e:
        print(f"Error fetching Lotto 6/49: {e}")
        return 0

    added_count = 0
    cursor = conn.cursor()
    
    for item in results:
        period = str(item['期別'])
        draw_date = item['開獎日期'][:10]
        # Sort numbers for consistency
        winning_nums = ','.join(f"{x:02d}" for x in sorted(item['獎號']))
        special_num = item['特別號']
        
        # Check if already exists
        cursor.execute(
            "SELECT 1 FROM lottery_history WHERE game_code = 'lotto' AND draw_period = ?",
            (period,)
        )
        if cursor.fetchone() is None:
            cursor.execute(
                "INSERT INTO lottery_history (game_code, draw_period, draw_date, winning_numbers, special_number) "
                "VALUES ('lotto', ?, ?, ?, ?)",
                (period, draw_date, winning_nums, special_num)
            )
            added_count += 1
            
    return added_count

def sync_daily_cash(conn):
    """Sync Taiwan Daily Cash 539 (今彩 539) data."""
    crawler = TaiwanLotteryCrawler()
    try:
        results = crawler.daily_cash()
    except Exception as e:
        print(f"Error fetching Daily Cash 539: {e}")
        return 0

    added_count = 0
    cursor = conn.cursor()
    
    for item in results:
        period = str(item['期別'])
        draw_date = item['開獎日期'][:10]
        winning_nums = ','.join(f"{x:02d}" for x in sorted(item['獎號']))
        
        # Check if already exists
        cursor.execute(
            "SELECT 1 FROM lottery_history WHERE game_code = 'daily_cash_539' AND draw_period = ?",
            (period,)
        )
        if cursor.fetchone() is None:
            cursor.execute(
                "INSERT INTO lottery_history (game_code, draw_period, draw_date, winning_numbers, special_number) "
                "VALUES ('daily_cash_539', ?, ?, ?, NULL)",
                (period, draw_date, winning_nums)
            )
            added_count += 1
            
    return added_count

def sync_mark_six(conn):
    """Sync Hong Kong Mark Six (六合彩) data from on99.life."""
    url = "https://on99.life/lottery/history/2026"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    try:
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code != 200:
            print(f"Error fetching Mark Six from on99.life: Status {r.status_code}")
            return 0
    except Exception as e:
        print(f"Error connecting to on99.life: {e}")
        return 0

    text = r.text
    keyword = '"results":['
    start_idx = text.find(keyword)
    if start_idx == -1:
        keyword = '\\"results\\":['
        start_idx = text.find(keyword)
        
    if start_idx == -1:
        print("Could not find results data on on99.life page.")
        return 0

    # Locate the opening bracket '[' of the results list
    bracket_start = start_idx + len(keyword) - 1
    bracket_count = 0
    end_idx = -1
    
    for i in range(bracket_start, len(text)):
        if text[i] == '[':
            bracket_count += 1
        elif text[i] == ']':
            bracket_count -= 1
            if bracket_count == 0:
                end_idx = i + 1
                break
                
    if end_idx == -1:
        print("Error parsing brackets for Mark Six results.")
        return 0

    results_str = text[bracket_start:end_idx]
    if '\\"' in results_str:
        results_str = results_str.replace('\\"', '"')

    try:
        results = json.loads(results_str)
    except Exception as e:
        print(f"Error loading Mark Six JSON: {e}")
        return 0

    added_count = 0
    cursor = conn.cursor()
    
    for item in results:
        draw_date = item.get('drawDate')
        draw_id = item.get('drawId')
        winning_nums_list = item.get('winningNumbers')
        special_num = item.get('extraNumber')
        
        if not draw_date or not draw_id or not winning_nums_list:
            continue
            
        # Format period like: '2026061' from '26/061'
        period = '20' + draw_id.replace('/', '')
        winning_nums = ','.join(f"{x:02d}" for x in sorted(winning_nums_list))
        
        # Check if already exists
        cursor.execute(
            "SELECT 1 FROM lottery_history WHERE game_code = 'mark_six' AND draw_period = ?",
            (period,)
        )
        if cursor.fetchone() is None:
            cursor.execute(
                "INSERT INTO lottery_history (game_code, draw_period, draw_date, winning_numbers, special_number) "
                "VALUES ('mark_six', ?, ?, ?, ?)",
                (period, draw_date, winning_nums, special_num)
            )
            added_count += 1
            
    return added_count

def sync_all_lotteries():
    """Sync all supported lottery data and return counts of new records added."""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    
    try:
        lotto_added = sync_lotto(conn)
        daily_cash_added = sync_daily_cash(conn)
        mark_six_added = sync_mark_six(conn)
        conn.commit()
        
        return {
            'lotto': lotto_added,
            'daily_cash_539': daily_cash_added,
            'mark_six': mark_six_added
        }
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

if __name__ == '__main__':
    print("Running standalone sync...")
    try:
        counts = sync_all_lotteries()
        print(f"Sync complete! Added: {counts}")
    except Exception as ex:
        print(f"Sync failed: {ex}")
