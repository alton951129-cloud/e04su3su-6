from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from app.models.user import UserModel

# 建立 F-05 專屬的 Blueprint，命名為 auth
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """處理使用者註冊流程。"""
    # 登入狀態下不允許註冊，重導至首頁
    if session.get('user_id'):
        return redirect(url_for('lottery.dashboard', game_code='lotto'))
        
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        # 欄位基本驗證
        if not username or not password or not confirm_password:
            flash("請填寫所有欄位！", "warning")
            return render_template('auth/register.html')
            
        if len(username) < 3 or len(username) > 20:
            flash("使用者名稱長度必須在 3 到 20 個字元之間！", "warning")
            return render_template('auth/register.html')
            
        if len(password) < 6:
            flash("密碼長度必須大於或等於 6 個字元！", "warning")
            return render_template('auth/register.html')
            
        if password != confirm_password:
            flash("兩次輸入的密碼不一致！", "warning")
            return render_template('auth/register.html')
            
        # 建立使用者帳戶
        success = UserModel.create(username, password)
        if success:
            flash("帳號註冊成功！請登入您的新帳戶。", "success")
            return redirect(url_for('auth.login'))
        else:
            flash("該使用者名稱已被註冊，請換一個名字！", "danger")
            
    return render_template('auth/register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """處理使用者登入流程。"""
    # 登入狀態下不允許登入，重導至首頁
    if session.get('user_id'):
        return redirect(url_for('lottery.dashboard', game_code='lotto'))
        
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        # 欄位基本驗證
        if not username or not password:
            flash("請填寫帳號與密碼！", "warning")
            return render_template('auth/login.html')
            
        # 查詢使用者並驗證密碼
        user = UserModel.get_by_username(username)
        if user and UserModel.verify_password(user, password):
            # 建立會話，寫入 session
            session.clear()
            session['user_id'] = user['id']
            session['username'] = user['username']
            flash(f"歡迎回來，{user['username']}！登入成功。", "success")
            return redirect(url_for('lottery.dashboard', game_code='lotto'))
        else:
            flash("使用者名稱或密碼錯誤，請重新確認！", "danger")
            
    return render_template('auth/login.html')

@auth_bp.route('/logout')
def logout():
    """處理使用者登出流程。"""
    session.clear()
    flash("您已成功登出系統，期待再次為您分析！", "success")
    return redirect(url_for('auth.login'))
