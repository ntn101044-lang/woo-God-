# routes/routes_weiyong.py
from flask import Blueprint, request, jsonify, session

# 從上一層 (..) 的 app.py 匯入資料庫實體與你需要用到的 Models
from app import db, Event, Visitor, QueueTicket, visitor_required

# 1. 宣告這是一張名為 'weiyong' 的藍圖 (Blueprint)
weiyong_bp = Blueprint('weiyong', __name__)

# ══════════════════════════════════════════════════════════════
# 為永的防區：活動資訊、遊客註冊、抽號碼牌
# ══════════════════════════════════════════════════════════════

# 【API 1：活動資訊】(注意：這裡變成 @weiyong_bp.route)
@weiyong_bp.route('/api/event/info', methods=['GET'])
def get_event_info():
    current_event = Event.query.first()
    if not current_event:
        return jsonify({'success': False, 'message': '目前沒有進行中的市集活動'}), 404

    event_data = {
        'event_id': current_event.event_id,
        'event_name': current_event.event_name,
        'start_date': current_event.start_date,
        'end_date': current_event.end_date,
        'map_image_url': current_event.map_image_url
    }
    return jsonify({'success': True, 'data': event_data}), 200

# 【API 2：遊客註冊】
@weiyong_bp.route('/visitor/register', methods=['POST'])
def visitor_register():
    data = request.get_json()
    account = data.get('account', '').strip()
    password = data.get('password', '')
    
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

# 【API 3：抽號碼牌 (大核心)】
@weiyong_bp.route('/ticket/draw', methods=['POST'])
@visitor_required
def draw_ticket():
    data = request.get_json()
    stall_id = data.get('stall_id')

    if not stall_id:
        return jsonify({'success': False, 'message': '缺少攤位 ID'}), 400

    max_ticket_record = QueueTicket.query.filter_by(stall_id=stall_id).order_by(QueueTicket.ticket_number.desc()).first()
    
    if max_ticket_record and max_ticket_record.ticket_number.isdigit():
        new_number = int(max_ticket_record.ticket_number) + 1
    else:
        new_number = 1

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
        'message': f'成功取得號碼牌！您是 {new_number} 號',
        'ticket': {
            'ticket_number': new_ticket_str,
            'expected_wait_time': wait_minutes,
            'stall_id': stall_id,
            'waiting_ahead': waiting_count
        }
    }), 201
