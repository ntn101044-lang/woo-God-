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
# Models
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
    status        = db.Column(db.String(20), default='active')  # 省略審核，直接 active
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
# 輔助
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
# 路由
# ══════════════════════════════════════════════════════════════

@app.route('/')
def index():
    role            = session.get('role', 'visitor')
    vendor_name     = session.get('vendor_name', '')
    visitor_account = session.get('visitor_account', '')
    return render_template('index.html', role=role,
                           vendor_name=vendor_name,
                           visitor_account=visitor_account)

# ── 攤主 ──────────────────────────────────────────────────────

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

# ── 攤主：商品管理 ─────────────────────────────────────────────

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

# ── 遊客 ──────────────────────────────────────────────────────

@app.route('/visitor/login', methods=['POST'])
def visitor_login():
    data    = request.get_json()
    visitor = Visitor.query.filter_by(account=data.get('account', '')).first()
    if visitor and visitor.check_password(data.get('password', '')):
        session.update({'role': 'visitor', 'visitor_id': visitor.visitor_id,
                        'visitor_account': visitor.account})
        return jsonify({'success': True, 'account': visitor.account})
    return jsonify({'success': False, 'message': '帳號或密碼錯誤'})

@app.route('/visitor/register', methods=['POST'])
def visitor_register():
    data    = request.get_json()
    account = data.get('account', '').strip()
    password= data.get('password', '')
    if not account or not password:
        return jsonify({'success': False, 'message': '請填寫帳號與密碼'})
    if Visitor.query.filter_by(account=account).first():
        return jsonify({'success': False, 'message': '此帳號已被使用'})
    v = Visitor(account=account)
    v.set_password(password)
    db.session.add(v)
    db.session.commit()
    session.update({'role': 'visitor', 'visitor_id': v.visitor_id, 'visitor_account': v.account})
    return jsonify({'success': True, 'account': v.account})

@app.route('/visitor/logout')
def visitor_logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/visitor/session')
def visitor_session():
    if session.get('visitor_id'):
        return jsonify({'logged_in': True, 'account': session.get('visitor_account', '')})
    return jsonify({'logged_in': False})

# ── 攤位 & 商品瀏覽 ───────────────────────────────────────────

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

# ── 訂單 ──────────────────────────────────────────────────────

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

@app.route('/market/info')
def market_info():
    today = datetime.now().strftime('%Y-%m-%d')
    now   = datetime.now()

    # 找今天正在進行的 event
    active_event = Event.query.filter(
        Event.start_date <= today,
        Event.end_date   >= today
    ).first()

    # 找下一場 event（未來最近的）
    next_event = Event.query.filter(
        Event.start_date > today
    ).order_by(Event.start_date.asc()).first()

    # 今日訂單數
    today_orders = Order.query.filter(
        Order.order_time.like(today + '%')
    ).count()

    # 活躍攤位數 & 總排隊人數
    active_stalls = Stall.query.filter_by(status='active').all()
    total_queue   = sum(
        QueueTicket.query.filter_by(stall_id=s.stall_id, status='waiting').count()
        for s in active_stalls
    )

    return jsonify({
        'active_event': {
            'event_name': active_event.event_name,
            'start_date': active_event.start_date,
            'end_date':   active_event.end_date,
        } if active_event else None,
        'next_event': {
            'event_name': next_event.event_name,
            'start_date': next_event.start_date,
            'end_date':   next_event.end_date,
        } if next_event else None,
        'stats': {
            'stall_count':  len(active_stalls),
            'total_queue':  total_queue,
            'today_orders': today_orders,
        }
    })
# ── 市集資訊 ──────────────────────────────────────────────────

@app.route('/market/info')
def market_info():
    today = datetime.now().strftime('%Y-%m-%d')

    active_event = Event.query.filter(
        Event.start_date <= today,
        Event.end_date   >= today
    ).first()

    next_event = Event.query.filter(
        Event.start_date > today
    ).order_by(Event.start_date.asc()).first()

    today_orders = Order.query.filter(
        Order.order_time.like(today + '%')
    ).count()

    active_stalls = Stall.query.filter_by(status='active').all()
    total_queue   = sum(
        QueueTicket.query.filter_by(stall_id=s.stall_id, status='waiting').count()
        for s in active_stalls
    )

    return jsonify({
        'active_event': {
            'event_name': active_event.event_name,
            'start_date': active_event.start_date,
            'end_date':   active_event.end_date,
        } if active_event else None,
        'next_event': {
            'event_name': next_event.event_name,
            'start_date': next_event.start_date,
            'end_date':   next_event.end_date,
        } if next_event else None,
        'stats': {
            'stall_count':  len(active_stalls),
            'total_queue':  total_queue,
            'today_orders': today_orders,
        }
    })

# ── Event 管理（簡易 admin，實際上線建議加密碼保護）────────────

@app.route('/admin/events', methods=['GET'])
def admin_events():
    events = Event.query.order_by(Event.start_date.desc()).all()
    return jsonify({'events': [{
        'event_id':   e.event_id,
        'event_name': e.event_name,
        'start_date': e.start_date,
        'end_date':   e.end_date,
    } for e in events]})

@app.route('/admin/events', methods=['POST'])
def admin_create_event():
    data = request.get_json()
    name  = data.get('event_name', '').strip()
    start = data.get('start_date', '').strip()
    end   = data.get('end_date', '').strip()
    if not name or not start or not end:
        return jsonify({'success': False, 'message': '請填寫所有欄位'})
    if start > end:
        return jsonify({'success': False, 'message': '結束日期不能早於開始日期'})
    e = Event(event_name=name, start_date=start, end_date=end)
    db.session.add(e)
    db.session.commit()
    return jsonify({'success': True, 'event': {
        'event_id': e.event_id, 'event_name': e.event_name,
        'start_date': e.start_date, 'end_date': e.end_date
    }})

@app.route('/admin/events/<event_id>', methods=['PATCH'])
def admin_update_event(event_id):
    e    = Event.query.get_or_404(event_id)
    data = request.get_json()
    if 'event_name' in data: e.event_name = data['event_name'].strip()
    if 'start_date' in data: e.start_date = data['start_date'].strip()
    if 'end_date'   in data: e.end_date   = data['end_date'].strip()
    if e.start_date > e.end_date:
        return jsonify({'success': False, 'message': '結束日期不能早於開始日期'})
    db.session.commit()
    return jsonify({'success': True})

@app.route('/admin/events/<event_id>', methods=['DELETE'])
def admin_delete_event(event_id):
    e = Event.query.get_or_404(event_id)
    db.session.delete(e)
    db.session.commit()
    return jsonify({'success': True})
# ══════════════════════════════════════════════════════════════
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)