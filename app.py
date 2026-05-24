from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from functools import wraps
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import uuid

# ══════════════════════════════════════════════════════════════
# 1. 系統核心配置與資料庫初始化
# ══════════════════════════════════════════════════════════════

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///market.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# ══════════════════════════════════════════════════════════════
# 2. 資料庫模型定義 (Models) - 由 db.create_all() 全自動轉譯成 SQL
# ══════════════════════════════════════════════════════════════

class Event(db.Model):
    __tablename__ = 'event'
    event_id      = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    event_name    = db.Column(db.String(100), nullable=False)
    start_date    = db.Column(db.String(20))
    end_date      = db.Column(db.String(20))
    map_image_url = db.Column(db.String(255))
    stalls        = db.relationship('Stall', backref='event', lazy=True)

class Vendor(db.Model):
    __tablename__ = 'vendor'
    vendor_id     = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    account       = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    name          = db.Column(db.String(50), nullable=False)
    phone         = db.Column(db.String(20))
    stall         = db.relationship('Stall', backref='vendor', uselist=False)
    def set_password(self, pw):   self.password_hash = generate_password_hash(pw)
    def check_password(self, pw): return check_password_hash(self.password_hash, pw)

# 多對多交集表：攤位與商品
offers = db.Table('offers',
    db.Column('stall_id',   db.String(36), db.ForeignKey('stall.stall_id'),    primary_key=True),
    db.Column('product_id', db.String(36), db.ForeignKey('product.product_id'), primary_key=True)
)

class Stall(db.Model):
    __tablename__ = 'stall'
    stall_id      = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    stall_name    = db.Column(db.String(100), nullable=False)
    zone_type     = db.Column(db.String(20))
    status        = db.Column(db.String(20), default='active')
    vendor_id     = db.Column(db.String(36), db.ForeignKey('vendor.vendor_id'), unique=True)
    event_id      = db.Column(db.String(36), db.ForeignKey('event.event_id'))
    products      = db.relationship('Product', secondary=offers, backref='stalls', lazy=True)
    queue_tickets = db.relationship('QueueTicket', backref='stall', lazy=True)
    orders        = db.relationship('Order', backref='stall', lazy=True)

class Visitor(db.Model):
    __tablename__ = 'visitor'
    visitor_id    = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    account       = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    queue_tickets = db.relationship('QueueTicket', backref='visitor', lazy=True)
    orders        = db.relationship('Order', backref='visitor', lazy=True)
    def set_password(self, pw):   self.password_hash = generate_password_hash(pw)
    def check_password(self, pw): return check_password_hash(self.password_hash, pw)

class Product(db.Model):
    __tablename__ = 'product'
    product_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name       = db.Column(db.String(100), nullable=False)
    price      = db.Column(db.Float, nullable=False)

class QueueTicket(db.Model):
    __tablename__      = 'queue_ticket'
    ticket_number      = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    status             = db.Column(db.String(20), default='waiting')
    expected_wait_time = db.Column(db.Integer)
    stall_id           = db.Column(db.String(36), db.ForeignKey('stall.stall_id'))
    visitor_id         = db.Column(db.String(36), db.ForeignKey('visitor.visitor_id'))

class Order(db.Model):
    __tablename__ = 'order'
    order_id   = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    order_time = db.Column(db.String(30))
    status     = db.Column(db.String(20), default='placed')
    visitor_id = db.Column(db.String(36), db.ForeignKey('visitor.visitor_id'))
    stall_id   = db.Column(db.String(36), db.ForeignKey('stall.stall_id'))
    items      = db.relationship('Includes', backref='order', lazy=True)

class Includes(db.Model):
    __tablename__ = 'includes'
    order_id   = db.Column(db.String(36), db.ForeignKey('order.order_id'),     primary_key=True)
    product_id = db.Column(db.String(36), db.ForeignKey('product.product_id'), primary_key=True)
    quantity   = db.Column(db.Integer, nullable=False, default=1)
    sold_price = db.Column(db.Float, nullable=False)

# ══════════════════════════════════════════════════════════════
# 3. 權限驗證與資料轉換輔助工具 (Helpers)
# ══════════════════════════════════════════════════════════════

def vendor_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if session.get('role') != 'vendor':
            return jsonify({'success': False, 'message': '請先登入'}), 401
        return f(*args, **kwargs)
    return decorated

def visitor_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if session.get('role') != 'visitor' or not session.get('visitor_id'):
            return jsonify({'success': False, 'message': '請先登入', 'need_login': True}), 401
        return f(*args, **kwargs)
    return decorated

def order_to_dict(o):
    visitor  = Visitor.query.get(o.visitor_id)
    products = []
    total    = 0
    for i in o.items:
        p    = Product.query.get(i.product_id)
        sub  = i.sold_price * i.quantity
        total += sub
        products.append({'name': p.name if p else '?',
                         'quantity': i.quantity, 'sold_price': i.sold_price, 'subtotal': sub})
    return {
        'order_id':        o.order_id,
        'order_time':      o.order_time,
        'status':          o.status,
        'stall_name':      o.stall.stall_name if o.stall else '',
        'visitor_account': visitor.account if visitor else '',
        'items':           products,
        'total':           total
    }

# ══════════════════════════════════════════════════════════════
# 4. 共用基礎路由 (其餘防區尚未拆分前暫留於此)
# ══════════════════════════════════════════════════════════════

@app.route('/')
def index():
    role            = session.get('role', 'visitor')
    vendor_name     = session.get('vendor_name', '')
    visitor_account = session.get('visitor_account', '')
    return render_template('index.html', role=role,
                           vendor_name=vendor_name,
                           visitor_account=visitor_account)

# ── 攤主登入與基本管理 ──
@app.route('/vendor/login', methods=['POST'])
def vendor_login():
    data    = request.get_json()
    vendor  = Vendor.query.filter_by(account=data.get('username', '')).first()
    if vendor and vendor.check_password(data.get('password', '')):
        session.update({'role': 'vendor', 'vendor_id': vendor.vendor_id, 'vendor_name': vendor.name})
        return jsonify({'success': True, 'name': vendor.name})
    return jsonify({'success': False, 'message': '帳號或密碼錯誤'})

@app.route('/vendor/logout')
def vendor_logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/vendor/stall', methods=['GET', 'POST'])
@vendor_required
def vendor_stall():
    vendor_id = session['vendor_id']
    if request.method == 'POST':
        data     = request.get_json()
        existing = Stall.query.filter_by(vendor_id=vendor_id).first()
        if existing:
            return jsonify({'success': False, 'message': '您已有攤位'})
        stall = Stall(stall_name=data.get('stall_name'), zone_type=data.get('zone_type'),
                      status='active', vendor_id=vendor_id)
        db.session.add(stall)
        db.session.commit()
        return jsonify({'success': True, 'stall': {
            'stall_id': stall.stall_id, 'stall_name': stall.stall_name,
            'zone_type': stall.zone_type, 'status': stall.status}})
    stall = Stall.query.filter_by(vendor_id=vendor_id).first()
    if not stall:
        return jsonify({'stall': None})
    return jsonify({'stall': {'stall_id': stall.stall_id, 'stall_name': stall.stall_name,
                              'zone_type': stall.zone_type, 'status': stall.status}})

# ── 攤主：商品管理 ──
@app.route('/vendor/products', methods=['GET'])
@vendor_required
def vendor_products():
    stall = Stall.query.filter_by(vendor_id=session['vendor_id']).first()
    if not stall:
        return jsonify({'products': [], 'has_stall': False})
    products = [{'product_id': p.product_id, 'name': p.name, 'price': p.price}
                for p in stall.products]
    return jsonify({'products': products, 'has_stall': True,
                    'stall_id': stall.stall_id, 'stall_name': stall.stall_name})

@app.route('/vendor/products', methods=['POST'])
@vendor_required
def vendor_add_product():
    stall = Stall.query.filter_by(vendor_id=session['vendor_id']).first()
    if not stall:
        return jsonify({'success': False, 'message': '請先建立攤位'})
    data = request.get_json()
    name  = data.get('name', '').strip()
    price = data.get('price')
    if not name or price is None:
        return jsonify({'success': False, 'message': '請填寫商品名稱與價格'})
    try:
        price = float(price)
        if price < 0: raise ValueError
    except ValueError:
        return jsonify({'success': False, 'message': '價格格式錯誤'})
    p = Product(name=name, price=price)
    db.session.add(p)
    db.session.flush()
    stall.products.append(p)
    db.session.commit()
    return jsonify({'success': True, 'product': {'product_id': p.product_id, 'name': p.name, 'price': p.price}})

@app.route('/vendor/products/<product_id>', methods=['DELETE'])
@vendor_required
def vendor_delete_product(product_id):
    stall = Stall.query.filter_by(vendor_id=session['vendor_id']).first()
    if not stall:
        return jsonify({'success': False, 'message': '找不到攤位'})
    product = Product.query.get_or_404(product_id)
    if product not in stall.products:
        return jsonify({'success': False, 'message': '此商品不屬於您的攤位'}), 403
    stall.products.remove(product)
    db.session.commit()
    return jsonify({'success': True})

# ── 遊客基礎通用路由 ──
@app.route('/visitor/login', methods=['POST'])
def visitor_login():
    data    = request.get_json()
    visitor = Visitor.query.filter_by(account=data.get('account', '')).first()
    if visitor and visitor.check_password(data.get('password', '')):
        session.update({'role': 'visitor', 'visitor_id': visitor.visitor_id,
                        'visitor_account': visitor.account})
        return jsonify({'success': True, 'account': visitor.account})
    return jsonify({'success': False, 'message': '帳號或密碼錯誤'})

@app.route('/visitor/logout')
def visitor_logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/visitor/session')
def visitor_session():
    if session.get('visitor_id'):
        return jsonify({'logged_in': True, 'account': session.get('visitor_account', '')})
    return jsonify({'logged_in': False})

# ── 攤位 & 商品瀏覽 ──
@app.route('/stalls')
def stall_list():
    stalls = Stall.query.filter_by(status='active').all()
    result = []
    for s in stalls:
        q = QueueTicket.query.filter_by(stall_id=s.stall_id, status='waiting').count()
        result.append({'stall_id': s.stall_id, 'stall_name': s.stall_name,
                       'zone_type': s.zone_type, 'queue_count': q, 'wait_minutes': q * 3})
    result.sort(key=lambda x: x['queue_count'], reverse=True)
    return jsonify({'stalls': result})

@app.route('/stall/<stall_id>/products')
def stall_products(stall_id):
    stall    = Stall.query.get_or_404(stall_id)
    products = [{'product_id': p.product_id, 'name': p.name, 'price': p.price}
                for p in stall.products]
    return jsonify({'stall_id': stall.stall_id, 'stall_name': stall.stall_name,
                    'zone_type': stall.zone_type, 'products': products})

# ── 預點餐訂單系統 ──
@app.route('/order/place', methods=['POST'])
@visitor_required
def place_order():
    data     = request.get_json()
    stall_id = data.get('stall_id')
    items    = data.get('items', [])
    if not stall_id or not items:
        return jsonify({'success': False, 'message': '訂單資料不完整'})
    order = Order(order_time=datetime.now().strftime('%Y-%m-%d %H:%M'),
                  status='placed', visitor_id=session['visitor_id'], stall_id=stall_id)
    db.session.add(order)
    db.session.flush()
    for item in items:
        p = Product.query.get(item['product_id'])
        if not p: continue
        db.session.add(Includes(order_id=order.order_id, product_id=p.product_id,
                                quantity=item.get('quantity', 1), sold_price=p.price))
    db.session.commit()
    return jsonify({'success': True, 'order_id': order.order_id})

@app.route('/visitor/orders')
@visitor_required
def visitor_orders():
    orders = Order.query.filter_by(visitor_id=session['visitor_id'])\
                        .order_by(Order.order_time.desc()).all()
    return jsonify({'orders': [order_to_dict(o) for o in orders]})

@app.route('/vendor/orders')
@vendor_required
def vendor_orders():
    stall = Stall.query.filter_by(vendor_id=session['vendor_id']).first()
    if not stall:
        return jsonify({'orders': []})
    orders = Order.query.filter_by(stall_id=stall.stall_id)\
                        .order_by(Order.order_time.desc()).all()
    return jsonify({'orders': [order_to_dict(o) for o in orders]})

@app.route('/order/<order_id>/status', methods=['PATCH'])
@vendor_required
def update_order_status(order_id):
    NEXT = {'placed': 'confirming', 'confirming': 'making', 'making': 'ready', 'ready': 'completed'}
    data   = request.get_json()
    new_st = data.get('status')
    order  = Order.query.get_or_404(order_id)
    stall  = Stall.query.filter_by(vendor_id=session['vendor_id']).first()
    if not stall or order.stall_id != stall.stall_id:
        return jsonify({'success': False, 'message': '無權限'}), 403
    if new_st == 'cancelled' or new_st == NEXT.get(order.status):
        order.status = new_st
        db.session.commit()
        return jsonify({'success': True, 'status': order.status})
    return jsonify({'success': False, 'message': f'無法從 {order.status} 改為 {new_st}'})

# ══════════════════════════════════════════════════════════════
# 5. 🔥 核心亮點：動態掛載模組藍圖 (Blueprints Registration)
# ══════════════════════════════════════════════════════════════

# 💡 物理意義：這段必須放在 Models 下方。當此處執行 import 時，
# 你的 routes_weiyong.py 就能順利回頭抓到上面已經定義完成的 db、Visitor、Event 等強大資源。
from routes.routes_weiyong import weiyong_bp

# 正式向系統核心註冊你的專屬模組延長線
app.register_blueprint(weiyong_bp)

# ══════════════════════════════════════════════════════════════
# 6. 系統主程式啟動點
# ══════════════════════════════════════════════════════════════
if __name__ == '__main__':
    with app.app_context():
        # ORM 自動掃描上述所有 class 結構，全自動建立 SQLite 表格
        db.create_all()
    app.run(debug=True)
