import datetime
from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from app.models.game import GameModel
from app.models.record import RecordModel

# 建立 F-04 專屬的 Blueprint，命名為 record
record_bp = Blueprint('record', __name__)

@record_bp.route('/records')
def list_records():
    """顯示個人投注記帳清單與財務數據分析大盤。"""
    user_id = session.get('user_id')
    if not user_id:
        flash("請先登入帳號以使用個人投注記帳功能！", "warning")
        return redirect(url_for('auth.login'))
        
    # 獲取系統支援的所有彩券種類
    all_games = GameModel.get_all()
    
    # 獲取使用者的所有歷史投注紀錄
    records = RecordModel.get_by_user(user_id)
    
    # 獲取使用者的累計投注財務數據
    stats = RecordModel.get_stats_by_user(user_id)
    
    # 預填今天的日期
    today_date = datetime.date.today().strftime('%Y-%m-%d')
    
    return render_template(
        'lottery/records.html',
        all_games=all_games,
        records=records,
        stats=stats,
        today_date=today_date
    )

@record_bp.route('/records/add', methods=['POST'])
def add_record():
    """新增一筆投注盈虧紀錄。"""
    user_id = session.get('user_id')
    if not user_id:
        flash("請先登入帳號！", "warning")
        return redirect(url_for('auth.login'))
        
    game_code = request.form.get('game_code', '').strip()
    cost_str = request.form.get('cost', '').strip()
    prize_str = request.form.get('prize', '').strip()
    record_date = request.form.get('record_date', '').strip()
    
    # 欄位基本驗證
    if not game_code or not cost_str or not prize_str or not record_date:
        flash("所有欄位皆為必填項目！", "warning")
        return redirect(url_for('record.list_records'))
        
    try:
        cost = int(cost_str)
        prize = int(prize_str)
    except ValueError:
        flash("投注金額與中獎金額必須為整數！", "warning")
        return redirect(url_for('record.list_records'))
        
    if cost <= 0:
        flash("投注花費金額必須大於 0 元！", "warning")
        return redirect(url_for('record.list_records'))
        
    if prize < 0:
        flash("中獎金額不能為負數！", "warning")
        return redirect(url_for('record.list_records'))
        
    # 驗證日期格式 YYYY-MM-DD
    try:
        datetime.datetime.strptime(record_date, '%Y-%m-%d')
    except ValueError:
        flash("日期格式不正確，應為 YYYY-MM-DD！", "warning")
        return redirect(url_for('record.list_records'))
        
    # 呼叫 Model 寫入資料庫
    success = RecordModel.create(user_id, game_code, cost, prize, record_date)
    if success:
        flash("記帳明細已成功新增！", "success")
    else:
        flash("記帳失敗，請稍後再試！", "danger")
        
    return redirect(url_for('record.list_records'))

@record_bp.route('/records/<int:id>/delete', methods=['POST'])
def delete_record(id):
    """安全刪除使用者的投注紀錄。"""
    user_id = session.get('user_id')
    if not user_id:
        flash("請先登入帳號！", "warning")
        return redirect(url_for('auth.login'))
        
    # 呼叫 Model 進行安全刪除
    success = RecordModel.delete(id, user_id)
    if success:
        flash("投注明細已成功刪除！", "success")
    else:
        flash("刪除失敗：該紀錄可能已被刪除或您沒有權限進行此操作！", "danger")
        
    return redirect(url_for('record.list_records'))
