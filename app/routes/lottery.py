from flask import Blueprint, render_template, abort, redirect, url_for
from app.models.game import GameModel
from app.models.history import HistoryModel

# 建立 F-03 專屬的 Blueprint，命名為 lottery
lottery_bp = Blueprint('lottery', __name__)

@lottery_bp.route('/lottery/<game_code>')
def dashboard(game_code):
    """大盤核心視圖：切換並顯示選定彩券的統計數據與推薦生成。"""
    # 1. 取得當前選定的彩券規則
    current_game = GameModel.get_by_code(game_code)
    if not current_game:
        # 若找不到此種類，重導向至大樂透預設頁面，防掛掉
        return redirect(url_for('lottery.dashboard', game_code='lotto'))

    # 2. 獲取系統支援的所有彩券列表 (供頂部導航卡片切換)
    all_games = GameModel.get_all()

    # 3. 獲取該彩券最近的開獎紀錄 (最近 10 期)
    history_draws = HistoryModel.get_recent_draws(game_code, limit=10)

    # 4. 獲取該彩券的號碼冷熱門頻率統計
    stats = HistoryModel.get_number_frequency(game_code)

    # 5. 渲染精美的 Jinja2 模板
    return render_template(
        'lottery/dashboard.html',
        current_game=current_game,
        all_games=all_games,
        history=history_draws,
        stats=stats
    )
