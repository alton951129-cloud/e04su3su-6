from flask import Flask, render_template, jsonify
from database import init_db, get_db_connection
import sqlite3

app = Flask(__name__)

# 初始化資料庫與種子數據
init_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/lottery/history/<game>')
def get_lottery_history(game):
    valid_games = ['big_lotto', 'super_lotto', 'daily_cash_539']
    if game not in valid_games:
        return jsonify({'success': False, 'message': '不支援此彩券種類'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 獲取最近 50 期的開獎歷史，最新的在最前面
        cursor.execute(f"SELECT * FROM {game} ORDER BY draw_date DESC, draw_number DESC LIMIT 50")
        rows = cursor.fetchall()
        
        history = []
        for row in rows:
            data = {
                'id': row['id'],
                'draw_date': row['draw_date'],
                'draw_number': row['draw_number']
            }
            # 根據彩券類型整理號碼
            if game == 'big_lotto':
                data['numbers'] = [row['n1'], row['n2'], row['n3'], row['n4'], row['n5'], row['n6']]
                data['special_num'] = row['s_num']
            elif game == 'super_lotto':
                data['numbers'] = [row['n1'], row['n2'], row['n3'], row['n4'], row['n5'], row['n6']]
                data['special_num'] = row['s2_num']
            elif game == 'daily_cash_539':
                data['numbers'] = [row['n1'], row['n2'], row['n3'], row['n4'], row['n5']]
                data['special_num'] = None
                
            history.append(data)
            
        return jsonify({'success': True, 'game': game, 'data': history})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        conn.close()

@app.route('/api/lottery/stats/<game>')
def get_lottery_stats(game):
    valid_games = ['big_lotto', 'super_lotto', 'daily_cash_539']
    if game not in valid_games:
        return jsonify({'success': False, 'message': '不支援此彩券種類'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 獲取歷史所有開獎數據做統計分析
        cursor.execute(f"SELECT * FROM {game} ORDER BY draw_date DESC")
        rows = cursor.fetchall()
        
        if not rows:
            return jsonify({'success': True, 'game': game, 'frequencies': {}, 'hot_numbers': [], 'cold_numbers': []})

        # 定義數字範圍
        if game == 'big_lotto':
            num_range = range(1, 50)
            spec_range = range(1, 50)
        elif game == 'super_lotto':
            num_range = range(1, 39)
            spec_range = range(1, 9)
        elif game == 'daily_cash_539':
            num_range = range(1, 40)
            spec_range = None

        # 頻率統計
        freq = {i: 0 for i in num_range}
        spec_freq = {i: 0 for i in spec_range} if spec_range else None
        
        odd_count = 0
        even_count = 0
        total_sum = 0
        total_balls_count = 0
        
        # 逐筆統計
        for row in rows:
            if game == 'big_lotto':
                nums = [row['n1'], row['n2'], row['n3'], row['n4'], row['n5'], row['n6']]
                s_num = row['s_num']
                spec_freq[s_num] = spec_freq.get(s_num, 0) + 1
            elif game == 'super_lotto':
                nums = [row['n1'], row['n2'], row['n3'], row['n4'], row['n5'], row['n6']]
                s2_num = row['s2_num']
                spec_freq[s2_num] = spec_freq.get(s2_num, 0) + 1
            elif game == 'daily_cash_539':
                nums = [row['n1'], row['n2'], row['n3'], row['n4'], row['n5']]

            # 統計號碼頻率、總和與奇偶
            for n in nums:
                if n in freq:
                    freq[n] += 1
                odd_count += 1 if n % 2 != 0 else 0
                even_count += 1 if n % 2 == 0 else 0
                total_sum += n
                total_balls_count += 1

        # 找出熱門/冷門號碼
        sorted_nums = sorted(freq.items(), key=lambda x: x[1], reverse=True)
        hot_numbers = [item[0] for item in sorted_nums[:5]]
        cold_numbers = [item[0] for item in sorted_nums[-5:]]
        
        # 計算平均和 (每期開出號碼的總和平均)
        draws_count = len(rows)
        avg_sum = round(total_sum / draws_count, 2) if draws_count > 0 else 0
        
        # 未開出期數分析 (Gap/Omission) - 計算每個號碼自上一次被開出到現在隔了幾期
        omissions = {i: 0 for i in num_range}
        for n in num_range:
            gap = 0
            found = False
            for idx, row in enumerate(rows):
                if game in ('big_lotto', 'super_lotto'):
                    nums = [row['n1'], row['n2'], row['n3'], row['n4'], row['n5'], row['n6']]
                else:
                    nums = [row['n1'], row['n2'], row['n3'], row['n4'], row['n5']]
                    
                if n in nums:
                    omissions[n] = gap
                    found = True
                    break
                gap += 1
            if not found:
                omissions[n] = draws_count # 從未開出，則記為全部期數

        response_data = {
            'success': True,
            'game': game,
            'draws_count': draws_count,
            'frequencies': freq,
            'special_frequencies': spec_freq,
            'hot_numbers': hot_numbers,
            'cold_numbers': cold_numbers,
            'odd_count': odd_count,
            'even_count': even_count,
            'average_sum': avg_sum,
            'omissions': omissions
        }
        
        return jsonify(response_data)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        conn.close()

if __name__ == '__main__':
    app.run(debug=True)

