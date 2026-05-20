from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from functools import wraps
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import uuid

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///market.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# ══════════════════════════════════════════════════════════════
# Models（未更動）
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


offers = db.Table('offers',
    db.Column('stall_id',   db.String(36), db.ForeignKey('stall.stall_id'),    primary_key=True),
    db.Column('product_id', db.String(36), db.ForeignKey('product.product_id'), primary_key=True)
)


class Stall(db.Model):
    __tablename__ = 'stall'
    stall_id      = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    stall_name    = db.Column(db.String(100), nullable=False)
    zone_type     = db.Column(db.String(20))
    status        = db.Column(db.String(20), default='pending')
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
    # ╔══════════════════════════════════════════════════════════╗
    # ║ 【已更動】status 新增 confirming/making/ready 等細分狀態 ║
    # ╚══════════════════════════════════════════════════════════╝
    status     = db.Column(db.String(20), default='placed')
    # placed → confirming → making → ready → completed / cancelled
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
# 輔助函式
# ══════════════════════════════════════════════════════════════

def vendor_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if session.get('role') != 'vendor':
            return jsonify({'success': False, 'message': '請先登入'}), 401
        return f(*args, **kwargs)
    return decorated

# ╔══════════════════════════════════════════════════════════════╗
# ║ 【新增】遊客登入驗證裝飾器                                    ║
# ╚══════════════════════════════════════════════════════════════╝
def visitor_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if session.get('role') != 'visitor' or not session.get('visitor_id'):
            return jsonify({'success': False, 'message': '請先登入', 'need_login': True}), 401
        return f(*args, **kwargs)
    return decorated


# ══════════════════════════════════════════════════════════════
# 路由
# ══════════════════════════════════════════════════════════════

@app.route('/')
def index():
    role        = session.get('role', 'visitor')
    vendor_name = session.get('vendor_name', '')
    visitor_account = session.get('visitor_account', '')
    return render_template('index.html', role=role,
                           vendor_name=vendor_name,
                           visitor_account=visitor_account)


# ── 攤主登入 / 登出 ────────────────────────────────────────────

@app.route('/vendor/login', methods=['POST'])
def vendor_login():
    data     = request.get_json()
    account  = data.get('username', '')
    password = data.get('password', '')
    vendor   = Vendor.query.filter_by(account=account).first()
    if vendor and vendor.check_password(password):
        session['role']        = 'vendor'
        session['vendor_id']   = vendor.vendor_id
        session['vendor_name'] = vendor.name
        return jsonify({'success': True, 'name': vendor.name})
    return jsonify({'success': False, 'message': '帳號或密碼錯誤'})


@app.route('/vendor/logout')
def vendor_logout():
    session.clear()
    return redirect(url_for('index'))


# ╔══════════════════════════════════════════════════════════════╗
# ║ 【新增】遊客登入 / 註冊 / 登出                               ║
# ╚══════════════════════════════════════════════════════════════╝

@app.route('/visitor/login', methods=['POST'])
def visitor_login():
    data     = request.get_json()
    account  = data.get('account', '')
    password = data.get('password', '')
    visitor  = Visitor.query.filter_by(account=account).first()
    if visitor and visitor.check_password(password):
        session['role']            = 'visitor'
        session['visitor_id']      = visitor.visitor_id
        session['visitor_account'] = visitor.account
        return jsonify({'success': True, 'account': visitor.account})
    return jsonify({'success': False, 'message': '帳號或密碼錯誤'})


@app.route('/visitor/register', methods=['POST'])
def visitor_register():
    data     = request.get_json()
    account  = data.get('account', '').strip()
    password = data.get('password', '')
    if not account or not password:
        return jsonify({'success': False, 'message': '請填寫帳號與密碼'})
    if Visitor.query.filter_by(account=account).first():
        return jsonify({'success': False, 'message': '此帳號已被使用'})
    v = Visitor(account=account)
    v.set_password(password)
    db.session.add(v)
    db.session.commit()
    session['role']            = 'visitor'
    session['visitor_id']      = v.visitor_id
    session['visitor_account'] = v.account
    return jsonify({'success': True, 'account': v.account})


@app.route('/visitor/logout')
def visitor_logout():
    session.clear()
    return redirect(url_for('index'))


# ── 攤主：建立攤位 ─────────────────────────────────────────────

@app.route('/vendor/stall', methods=['GET', 'POST'])
@vendor_required
def vendor_stall():
    vendor_id = session['vendor_id']
    if request.method == 'POST':
        data     = request.get_json()
        existing = Stall.query.filter_by(vendor_id=vendor_id).first()
        if existing:
            return jsonify({'success': False, 'message': '您已有攤位申請，請等待審核'})
        stall = Stall(stall_name=data.get('stall_name'),
                      zone_type=data.get('zone_type'),
                      status='pending', vendor_id=vendor_id)
        db.session.add(stall)
        db.session.commit()
        return jsonify({'success': True, 'stall': {
            'stall_id': stall.stall_id, 'stall_name': stall.stall_name,
            'zone_type': stall.zone_type, 'status': stall.status}})
    stall = Stall.query.filter_by(vendor_id=vendor_id).first()
    return jsonify({'stall': {'stall_id': stall.stall_id, 'stall_name': stall.stall_name,
        'zone_type': stall.zone_type, 'status': stall.status} if stall else None})


# ╔══════════════════════════════════════════════════════════════╗
# ║ 【新增】取得攤位的商品列表（給遊客點攤位時用）               ║
# ╚══════════════════════════════════════════════════════════════╝
@app.route('/stall/<stall_id>/products')
def stall_products(stall_id):
    stall = Stall.query.get_or_404(stall_id)
    products = [{
        'product_id': p.product_id,
        'name':       p.name,
        'price':      p.price
    } for p in stall.products]
    return jsonify({
        'stall_id':   stall.stall_id,
        'stall_name': stall.stall_name,
        'zone_type':  stall.zone_type,
        'products':   products
    })


# ╔══════════════════════════════════════════════════════════════╗
# ║ 【新增】遊客送出訂單                                         ║
# ╚══════════════════════════════════════════════════════════════╝
@app.route('/order/place', methods=['POST'])
@visitor_required
def place_order():
    data     = request.get_json()
    stall_id = data.get('stall_id')
    items    = data.get('items', [])   # [{product_id, quantity}]

    if not stall_id or not items:
        return jsonify({'success': False, 'message': '訂單資料不完整'})

    order = Order(
        order_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        status     = 'placed',
        visitor_id = session['visitor_id'],
        stall_id   = stall_id
    )
    db.session.add(order)
    db.session.flush()   # 取得 order_id

    for item in items:
        product = Product.query.get(item['product_id'])
        if not product:
            continue
        inc = Includes(
            order_id   = order.order_id,
            product_id = product.product_id,
            quantity   = item.get('quantity', 1),
            sold_price = product.price
        )
        db.session.add(inc)

    db.session.commit()
    return jsonify({'success': True, 'order_id': order.order_id})


# ╔══════════════════════════════════════════════════════════════╗
# ║ 【新增】遊客查詢自己的訂單                                   ║
# ╚══════════════════════════════════════════════════════════════╝
@app.route('/visitor/orders')
@visitor_required
def visitor_orders():
    orders = Order.query.filter_by(visitor_id=session['visitor_id'])\
                        .order_by(Order.order_time.desc()).all()
    result = []
    for o in orders:
        result.append({
            'order_id':   o.order_id,
            'order_time': o.order_time,
            'status':     o.status,
            'stall_name': o.stall.stall_name if o.stall else '',
            'items': [{
                'name':      Product.query.get(i.product_id).name,
                'quantity':  i.quantity,
                'sold_price': i.sold_price
            } for i in o.items]
        })
    return jsonify({'orders': result})


# ╔══════════════════════════════════════════════════════════════╗
# ║ 【新增】攤主查詢自己攤位的訂單                               ║
# ╚══════════════════════════════════════════════════════════════╝
@app.route('/vendor/orders')
@vendor_required
def vendor_orders():
    stall = Stall.query.filter_by(vendor_id=session['vendor_id']).first()
    if not stall:
        return jsonify({'orders': []})
    orders = Order.query.filter_by(stall_id=stall.stall_id)\
                        .order_by(Order.order_time.desc()).all()
    result = []
    for o in orders:
        visitor = Visitor.query.get(o.visitor_id)
        result.append({
            'order_id':      o.order_id,
            'order_time':    o.order_time,
            'status':        o.status,
            'visitor_account': visitor.account if visitor else '',
            'items': [{
                'name':       Product.query.get(i.product_id).name,
                'quantity':   i.quantity,
                'sold_price': i.sold_price
            } for i in o.items]
        })
    return jsonify({'orders': result})


# ╔══════════════════════════════════════════════════════════════╗
# ║ 【新增】攤主更新訂單狀態                                     ║
# ╚══════════════════════════════════════════════════════════════╝
@app.route('/order/<order_id>/status', methods=['PATCH'])
@vendor_required
def update_order_status(order_id):
    VALID_TRANSITIONS = {
        'placed':      'confirming',
        'confirming':  'making',
        'making':      'ready',
        'ready':       'completed'
    }
    data      = request.get_json()
    new_status = data.get('status')
    order     = Order.query.get_or_404(order_id)

    # 確認這筆訂單屬於此攤主
    stall = Stall.query.filter_by(vendor_id=session['vendor_id']).first()
    if not stall or order.stall_id != stall.stall_id:
        return jsonify({'success': False, 'message': '無權限修改此訂單'}), 403

    # 允許取消，或按照正常流程推進
    if new_status == 'cancelled' or new_status == VALID_TRANSITIONS.get(order.status):
        order.status = new_status
        db.session.commit()
        return jsonify({'success': True, 'status': order.status})

    return jsonify({'success': False, 'message': f'無法從 {order.status} 改為 {new_status}'})


# ══════════════════════════════════════════════════════════════
# 初始化
# ══════════════════════════════════════════════════════════════

def init_db():
    db.create_all()
    if not Vendor.query.filter_by(account='vendor1').first():
        v = Vendor(account='vendor1', name='陳大明', phone='0912345678')
        v.set_password('1234')
        db.session.add(v)
        db.session.commit()
        print('✅ 測試攤主：vendor1 / 1234')
    if not Visitor.query.filter_by(account='visitor1').first():
        vis = Visitor(account='visitor1')
        vis.set_password('1234')
        db.session.add(vis)
        db.session.commit()
        print('✅ 測試遊客：visitor1 / 1234')


if __name__ == '__main__':
    with app.app_context():
        init_db()
    app.run(debug=True)