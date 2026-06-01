from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from functools import wraps
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import uuid
from sqlalchemy import text

# ══════════════════════════════════════════════════════════════
# 1. System Configuration & Database Initialization
# ══════════════════════════════════════════════════════════════

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///market.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# ══════════════════════════════════════════════════════════════
# 2. Database Models Definition
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
    # 修改：新增獨立的 ticket_id 作為主鍵，保證全系統唯一
    ticket_id          = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    # 修改：原本的 ticket_number 改為一般欄位
    ticket_number      = db.Column(db.String(36))
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
# 3. Middleware & Helpers
# ══════════════════════════════════════════════════════════════

def vendor_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if session.get('role') != 'vendor':
            return jsonify({'success': False, 'message': 'Please login as vendor first.'}), 401
        return f(*args, **kwargs)
    return decorated

def visitor_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if session.get('role') != 'visitor' or not session.get('visitor_id'):
            return jsonify({'success': False, 'message': 'Please login as visitor first.', 'need_login': True}), 401
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
# 4. Core Routes
# ══════════════════════════════════════════════════════════════

@app.route('/')
def index():
    role            = session.get('role', 'visitor')
    vendor_name     = session.get('vendor_name', '')
    visitor_account = session.get('visitor_account', '')
    return render_template('index.html', role=role,
                           vendor_name=vendor_name,
                           visitor_account=visitor_account)

# ── Vendor Routes ──
@app.route('/vendor/login', methods=['POST'])
def vendor_login():
    data    = request.get_json()
    vendor  = Vendor.query.filter_by(account=data.get('username', '')).first()
    if vendor and vendor.check_password(data.get('password', '')):
        session.update({'role': 'vendor', 'vendor_id': vendor.vendor_id, 'vendor_name': vendor.name})
        return jsonify({'success': True, 'name': vendor.name})
    return jsonify({'success': False, 'message': 'Invalid account or password.'})

@app.route('/vendor/register', methods=['POST'])
def vendor_register():
    data = request.get_json()
    name     = data.get('name', '').strip()
    account  = data.get('username', '').strip() 
    password = data.get('password', '')
    phone    = data.get('phone', '').strip()

    if not name or not account or not password or not phone:
        return jsonify({'success': False, 'message': 'Please fill in all registration fields.'})

    existing_vendor = Vendor.query.filter_by(account=account).first()
    if existing_vendor:
        return jsonify({'success': False, 'message': 'This account is already registered, please choose another.'})

    try:
        new_vendor = Vendor(account=account, name=name, phone=phone)
        new_vendor.set_password(password)

        db.session.add(new_vendor)
        db.session.commit()

        session.update({
            'role': 'vendor',
            'vendor_id': new_vendor.vendor_id,
            'vendor_name': new_vendor.name
        })
        return jsonify({'success': True, 'message': 'Registration successful!'})

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Database registration failed: {str(e)}'})

@app.route('/vendor/logout')
def vendor_logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/vendor/stall', methods=['GET', 'POST', 'DELETE'])
@vendor_required
def vendor_stall():
    vendor_id = session['vendor_id']
    
    if request.method == 'DELETE':
        stall = Stall.query.filter_by(vendor_id=vendor_id).first()
        if not stall:
            return jsonify({'success': False, 'message': 'Stall data not found.'})
        
        try:
            stall.products.clear() 
            db.session.delete(stall)
            db.session.commit()
            return jsonify({'success': True, 'message': 'Stall and associated products successfully deleted!'})
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'message': f'Database error: {str(e)}'})
        
    if request.method == 'POST':
        data     = request.get_json()
        existing = Stall.query.filter_by(vendor_id=vendor_id).first()
        if existing:
            return jsonify({'success': False, 'message': 'You already have a stall.'})
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

# ── Vendor Queue Management ──
@app.route('/vendor/queue', methods=['GET'])
@vendor_required
def vendor_queue():
    stall = Stall.query.filter_by(vendor_id=session['vendor_id']).first()
    if not stall:
        return jsonify({'success': False, 'message': 'Please create a stall first.', 'tickets': []})

    # 取得該攤位所有 waiting 狀態的號碼牌
    tickets = QueueTicket.query.filter_by(stall_id=stall.stall_id, status='waiting').all()
    
    # 修改：加入防呆機制，避免空值報錯
    tickets.sort(key=lambda x: int(x.ticket_number) if x.ticket_number and x.ticket_number.isdigit() else 0)
    
    result = []
    for t in tickets:
        visitor = Visitor.query.get(t.visitor_id)
        result.append({
            'ticket_number': t.ticket_number,
            'wait_time': t.expected_wait_time,
            'visitor_account': visitor.account if visitor else 'Unknown'
        })
        
    return jsonify({'success': True, 'tickets': result})

@app.route('/vendor/queue/<ticket_number>', methods=['PATCH'])
@vendor_required
def complete_queue_ticket(ticket_number):
    stall = Stall.query.filter_by(vendor_id=session['vendor_id']).first()
    if not stall:
        return jsonify({'success': False, 'message': 'Permission denied.'}), 403
        
    # 找出指定號碼牌並完成它
    ticket = QueueTicket.query.filter_by(stall_id=stall.stall_id, ticket_number=ticket_number, status='waiting').first()
    if ticket:
        ticket.status = 'completed'
        db.session.commit()
        return jsonify({'success': True})
    return jsonify({'success': False, 'message': 'Ticket not found or already processed.'})

# ── Vendor Products ──
@app.route('/vendor/products', methods=['GET'])
@vendor_required
def vendor_products():
    stall = Stall.query.filter_by(vendor_id=session['vendor_id']).first()
    if not stall:
        return jsonify({'products': [], 'has_stall': False})
    products = [{'product_id': p.product_id, 'name': p.name, 'price': p.price} for p in stall.products]
    return jsonify({'products': products, 'has_stall': True,
                    'stall_id': stall.stall_id, 'stall_name': stall.stall_name})

@app.route('/vendor/products', methods=['POST'])
@vendor_required
def vendor_add_product():
    stall = Stall.query.filter_by(vendor_id=session['vendor_id']).first()
    if not stall:
        return jsonify({'success': False, 'message': 'Please create a stall first.'})
    data = request.get_json()
    name  = data.get('name', '').strip()
    price = data.get('price')
    if not name or price is None:
        return jsonify({'success': False, 'message': 'Please provide product name and price.'})
    try:
        price = float(price)
        if price < 0: raise ValueError
    except ValueError:
        return jsonify({'success': False, 'message': 'Invalid price format.'})
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
        return jsonify({'success': False, 'message': 'Stall not found.'})
    product = Product.query.get_or_404(product_id)
    if product not in stall.products:
        return jsonify({'success': False, 'message': 'This product does not belong to your stall.'}), 403
    stall.products.remove(product)
    db.session.commit()
    return jsonify({'success': True})

@app.route('/vendor/products/<product_id>', methods=['PATCH'])
@vendor_required
def vendor_update_product(product_id):
    stall = Stall.query.filter_by(vendor_id=session['vendor_id']).first()
    if not stall:
        return jsonify({'success': False, 'message': 'Stall not found.'})
    
    product = Product.query.get_or_404(product_id)
    if product not in stall.products:
        return jsonify({'success': False, 'message': 'This product does not belong to your stall.'}), 403
        
    data = request.get_json()
    
    # 更新名稱與價格
    if 'name' in data and data['name'].strip():
        product.name = data['name'].strip()
    if 'price' in data:
        try:
            price = float(data['price'])
            if price < 0: raise ValueError
            product.price = price
        except ValueError:
            return jsonify({'success': False, 'message': 'Invalid price format.'})
            
    db.session.commit()
    return jsonify({'success': True})

# ── Visitor Routes ──
@app.route('/visitor/login', methods=['POST'])
def visitor_login():
    data    = request.get_json()
    visitor = Visitor.query.filter_by(account=data.get('account', '')).first()
    if visitor and visitor.check_password(data.get('password', '')):
        session.update({'role': 'visitor', 'visitor_id': visitor.visitor_id,
                        'visitor_account': visitor.account})
        return jsonify({'success': True, 'account': visitor.account})
    return jsonify({'success': False, 'message': 'Invalid account or password.'})

@app.route('/visitor/logout')
def visitor_logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/visitor/session')
def visitor_session():
    if session.get('visitor_id'):
        return jsonify({'logged_in': True, 'account': session.get('visitor_account', '')})
    return jsonify({'logged_in': False})

# ── Market & Stall Browsing ──
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
    products = [{'product_id': p.product_id, 'name': p.name, 'price': p.price} for p in stall.products]
    return jsonify({'stall_id': stall.stall_id, 'stall_name': stall.stall_name,
                    'zone_type': stall.zone_type, 'products': products})

# ── Ordering System ──
@app.route('/order/place', methods=['POST'])
@visitor_required
def place_order():
    data     = request.get_json()
    stall_id = data.get('stall_id')
    items    = data.get('items', [])
    if not stall_id or not items:
        return jsonify({'success': False, 'message': 'Incomplete order data.'})
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
    orders = Order.query.filter_by(visitor_id=session['visitor_id']).order_by(Order.order_time.desc()).all()
    return jsonify({'orders': [order_to_dict(o) for o in orders]})

@app.route('/vendor/orders')
@vendor_required
def vendor_orders():
    stall = Stall.query.filter_by(vendor_id=session['vendor_id']).first()
    if not stall:
        return jsonify({'orders': []})
    orders = Order.query.filter_by(stall_id=stall.stall_id).order_by(Order.order_time.desc()).all()
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
        return jsonify({'success': False, 'message': 'Permission denied.'}), 403
    if new_st == 'cancelled' or new_st == NEXT.get(order.status):
        order.status = new_st
        db.session.commit()
        return jsonify({'success': True, 'status': order.status})
    return jsonify({'success': False, 'message': f'Cannot change status from {order.status} to {new_st}.'})

@app.route('/market/info')
def market_info():
    today = datetime.now().strftime('%Y-%m-%d')
    active_event = Event.query.filter(Event.start_date <= today, Event.end_date >= today).first()
    next_event = Event.query.filter(Event.start_date > today).order_by(Event.start_date.asc()).first()
    today_orders = Order.query.filter(Order.order_time.like(today + '%')).count()
    active_stalls = Stall.query.filter_by(status='active').all()
    total_queue   = sum(QueueTicket.query.filter_by(stall_id=s.stall_id, status='waiting').count() for s in active_stalls)

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

# ── Event Management ──
@app.route('/admin/events', methods=['GET'])
def admin_events():
    events = Event.query.order_by(Event.start_date.desc()).all()
    return jsonify({'events': [{'event_id': e.event_id, 'event_name': e.event_name,
                                'start_date': e.start_date, 'end_date': e.end_date} for e in events]})

@app.route('/admin/events', methods=['POST'])
def admin_create_event():
    data = request.get_json()
    name  = data.get('event_name', '').strip()
    start = data.get('start_date', '').strip()
    end   = data.get('end_date', '').strip()
    if not name or not start or not end:
        return jsonify({'success': False, 'message': 'Please fill in all fields.'})
    if start > end:
        return jsonify({'success': False, 'message': 'End date cannot be earlier than start date.'})
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
        return jsonify({'success': False, 'message': 'End date cannot be earlier than start date.'})
    db.session.commit()
    return jsonify({'success': True})

@app.route('/admin/events/<event_id>', methods=['DELETE'])
def admin_delete_event(event_id):
    e = Event.query.get_or_404(event_id)
    db.session.delete(e)
    db.session.commit()
    return jsonify({'success': True})

# ══════════════════════════════════════════════════════════════
# 5. Weiyong's Logic (Integrated successfully)
# ══════════════════════════════════════════════════════════════

@app.route('/api/event/info', methods=['GET'])
def get_event_info():
    current_event = Event.query.first()
    if not current_event:
        return jsonify({'success': False, 'message': 'No active market event currently.'}), 404

    event_data = {
        'event_id': current_event.event_id,
        'event_name': current_event.event_name,
        'start_date': current_event.start_date,
        'end_date': current_event.end_date,
        'map_image_url': current_event.map_image_url
    }
    return jsonify({'success': True, 'data': event_data}), 200


@app.route('/visitor/register', methods=['POST'])
def visitor_register():
    data = request.get_json()
    account = data.get('account', '').strip()
    password = data.get('password', '')
    
    if not account or not password:
        return jsonify({'success': False, 'message': 'Please provide account and password.'})
        
    if Visitor.query.filter_by(account=account).first(): 
        return jsonify({'success': False, 'message': 'This account is already in use.'})
        
    v = Visitor(account=account)
    v.set_password(password)
    
    db.session.add(v)
    db.session.commit()
    
    session.update({'role': 'visitor', 'visitor_id': v.visitor_id, 'visitor_account': v.account})
    return jsonify({'success': True, 'account': v.account})


@app.route('/ticket/draw', methods=['POST'])
@visitor_required
def draw_ticket():
    data = request.get_json()
    stall_id = data.get('stall_id')

    if not stall_id:
        return jsonify({'success': False, 'message': 'Missing stall ID.'}), 400

    # 修改：修復字串排序 Bug，把所有號碼牌抓出來轉成數字，才能正確找到真正的最大值
    all_tickets = QueueTicket.query.filter_by(stall_id=stall_id).all()
    max_number = 0
    for t in all_tickets:
        if t.ticket_number and t.ticket_number.isdigit():
            num = int(t.ticket_number)
            if num > max_number:
                max_number = num

    new_number = max_number + 1
    new_ticket_str = str(new_number)
    
    waiting_count = QueueTicket.query.filter_by(stall_id=stall_id, status='waiting').count()
    wait_minutes = waiting_count * 3

    new_ticket = QueueTicket(
        ticket_number=new_ticket_str,
        status='waiting',
        expected_wait_time=wait_minutes,
        stall_id=stall_id,
        visitor_id=session['visitor_id']
    )

    db.session.add(new_ticket)
    db.session.commit()

    return jsonify({
        'success': True,
        'message': 'Ticket drawn successfully!',
        'ticket': {
            'ticket_number': new_ticket_str,
            'expected_wait_time': wait_minutes,
            'stall_id': stall_id,
            'waiting_ahead': waiting_count
        }
    }), 201

# ══════════════════════════════════════════════════════════════
# 6. Admin Dashboard (Fixed: Moved to correct place & uses SQLAlchemy)
# ══════════════════════════════════════════════════════════════

@app.route('/admin_dashboard')
def admin_dashboard():
    try:
        all_visitors = [{'VisitorID': v.visitor_id, 'Account': v.account} for v in Visitor.query.all()]
        all_vendors = [{'VendorID': v.vendor_id, 'VendorName': v.name, 'Phone': v.phone} for v in Vendor.query.all()]
        all_stalls = [{'StallID': s.stall_id, 'StallName': s.stall_name, 'ZoneType': s.zone_type, 'Status': s.status, 'VendorID': s.vendor_id, 'EventID': s.event_id} for s in Stall.query.all()]
        all_events = [{'EventID': e.event_id, 'EventName': e.event_name, 'StartDate': e.start_date, 'EndDate': e.end_date, 'MapImageURL': e.map_image_url} for e in Event.query.all()]
        all_tickets = [{'TicketNumber': t.ticket_number, 'WaitTime': t.expected_wait_time, 'Status': t.status, 'StallID': t.stall_id, 'VisitorID': t.visitor_id} for t in QueueTicket.query.all()]
        all_products = [{'ProductID': p.product_id, 'ProductName': p.name, 'Price': p.price} for p in Product.query.all()]
        all_orders = [{'OrderID': o.order_id, 'OrderTime': o.order_time, 'Status': o.status, 'VisitorID': o.visitor_id, 'StallID': o.stall_id, 'PaymentMethod': 'Cash'} for o in Order.query.all()]

        # Uses SQLAlchemy native execute mappings instead of `conn.cursor()`
        all_offers = [dict(row) for row in db.session.execute(text("SELECT stall_id as StallID, product_id as ProductID FROM offers")).mappings()]
        all_includes = [dict(row) for row in db.session.execute(text("SELECT order_id as OrderID, product_id as ProductID, quantity as Quantity, sold_price as SoldPrice FROM includes")).mappings()]
        
    except Exception as e:
        print(f"Database read error: {e}")
        all_visitors, all_vendors, all_stalls = [], [], []
        all_events, all_tickets, all_products = [], [], []
        all_orders, all_offers, all_includes = [], [], []

    return render_template(
        'admin.html', 
        visitors=all_visitors, vendors=all_vendors, stalls=all_stalls,
        events=all_events, tickets=all_tickets, products=all_products,
        orders=all_orders, offers=all_offers, includes=all_includes
    )

# ══════════════════════════════════════════════════════════════
# 7. System Startup
# ══════════════════════════════════════════════════════════════

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)