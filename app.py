from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from functools import wraps
 
app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this'
 
# ── 暫用假資料（之後換成資料庫） ──────────────────────────────
VENDORS = {
    'vendor1': {'password': '1234', 'name': '陳大明', 'vendor_id': 'V001'},
}
 
STALLS = {}  # stallID -> stall data
 
# ── 輔助函式 ───────────────────────────────────────────────────
def vendor_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if session.get('role') != 'vendor':
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated
 
# ── 路由 ───────────────────────────────────────────────────────
 
@app.route('/')
def index():
    """導覽頁：預設是遊客視角"""
    role = session.get('role', 'visitor')
    vendor_name = session.get('vendor_name', '')
    return render_template('index.html', role=role, vendor_name=vendor_name)
 
 
# ── 攤主登入 / 登出 ────────────────────────────────────────────
 
@app.route('/vendor/login', methods=['GET', 'POST'])
def vendor_login():
    if request.method == 'POST':
        data = request.get_json()
        username = data.get('username', '')
        password = data.get('password', '')
 
        vendor = VENDORS.get(username)
        if vendor and vendor['password'] == password:
            session['role'] = 'vendor'
            session['vendor_id'] = vendor['vendor_id']
            session['vendor_name'] = vendor['name']
            return jsonify({'success': True, 'name': vendor['name']})
        return jsonify({'success': False, 'message': '帳號或密碼錯誤'})
 
    return jsonify({'error': 'use POST'}), 405
 
 
@app.route('/vendor/logout')
def vendor_logout():
    session.clear()
    return redirect(url_for('index'))
 
 
# ── 攤主：建立攤位 ─────────────────────────────────────────────
 
@app.route('/vendor/stall', methods=['GET', 'POST'])
@vendor_required
def vendor_stall():
    vendor_id = session['vendor_id']
 
    if request.method == 'POST':
        data = request.get_json()
        stall = {
            'stall_id': f"S{len(STALLS)+1:03d}",
            'vendor_id': vendor_id,
            'stall_name': data.get('stall_name'),
            'zone_type': data.get('zone_type'),
            'status': 'pending',   # 需管理員審核
            'products': []
        }
        STALLS[stall['stall_id']] = stall
        return jsonify({'success': True, 'stall': stall})
 
    # GET：回傳該攤主的攤位資料
    my_stall = next((s for s in STALLS.values() if s['vendor_id'] == vendor_id), None)
    return jsonify({'stall': my_stall})
 
 
if __name__ == '__main__':
    app.run(debug=True)