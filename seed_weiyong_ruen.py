# seed_total.py (連號碼牌一起抽好版)
from app import app, db, Event, Visitor, Vendor, Stall, Product, QueueTicket, offers
from datetime import datetime

def seed_all_tables():
    with app.app_context():
        print("==================================================")
        print("【全系統初始化】開始清理舊資料，確保不重複插入...")
        print("==================================================")
        
        # ⚠️ 加上 QueueTicket 的清理
        QueueTicket.query.delete()
        db.session.execute(offers.delete())
        Stall.query.delete()
        Vendor.query.delete()
        Product.query.delete()
        Visitor.query.delete()
        Event.query.delete()

        # ══════════════════════════════════════════════════════════════
        # 1. 偉詠的防區：建立市集活動與遊客 (Event & Visitor)
        # ══════════════════════════════════════════════════════════════
        print("\n[1/4] 正在建立活動與遊客資料...")
        
        target_event = Event(
            event_name="華山文創夏日風格市集",
            start_date="2026-07-10",
            end_date="2026-07-15",
            map_image_url="https://images.example.com/huashan_map.jpg"
        )
        db.session.add(target_event)
        
        visitor_1 = Visitor(account="taipei_user01@example.com")
        visitor_1.set_password("welcome2026")
        visitor_2 = Visitor(account="taipei_user02@example.com")
        visitor_2.set_password("hello2026")
        
        db.session.add(visitor_1)
        db.session.add(visitor_2)
        db.session.flush() 

        # ══════════════════════════════════════════════════════════════
        # 2. 如恩的防區：建立泰式奶茶攤位
        # ══════════════════════════════════════════════════════════════
        print("\n[2/4] 正在建立如恩泰式奶茶攤位...")
        
        vendor_1 = Vendor(
            account="ruen_tea@example.com",
            name="如恩正宗泰式奶茶",
            phone="0988777666"
        )
        vendor_1.set_password("ruentea123") 
        db.session.add(vendor_1)
        db.session.flush()

        stall_1 = Stall(
            stall_name="如恩泰奶 01 號攤",
            zone_type="飲品區",
            status="active",
            event_id=target_event.event_id,
            vendor_id=vendor_1.vendor_id
        )
        db.session.add(stall_1)
        db.session.flush()

        # ══════════════════════════════════════════════════════════════
        # 3. 商品與上架功能測試
        # ══════════════════════════════════════════════════════════════
        print("\n[3/4] 正在上架泰奶菜單...")
        product_1 = Product(name="手標正宗泰式奶茶", price=70.0)
        db.session.add(product_1)
        db.session.flush()
        stall_1.products.append(product_1)

        # ══════════════════════════════════════════════════════════════
        # 4. 🔥 全新追加：模擬遊客來「抽號碼牌 (QueueTicket)」
        # ══════════════════════════════════════════════════════════════
        print("\n[4/4] 🚀 正在模擬遊客線上抽號碼牌...")
        
        # 讓台北遊客 1 號，去抽如恩泰奶攤位的號碼牌
        ticket_1 = QueueTicket(
            status="waiting",
            expected_wait_time=15,          # 預計等 15 分鐘
            stall_id=stall_1.stall_id,      # 🔗 連結如恩的攤位 UUID
            visitor_id=visitor_1.visitor_id # 🔗 連結偉詠的遊客 UUID
        )
        
        # 讓台北遊客 2 號，也去抽同一個攤位
        ticket_2 = QueueTicket(
            status="waiting",
            expected_wait_time=30,          # 預計等 30 分鐘
            stall_id=stall_1.stall_id,
            visitor_id=visitor_2.visitor_id
        )
        
        db.session.add(ticket_1)
        db.session.add(ticket_2)

        # ══════════════════════════════════════════════════════════════
        # 5. 正式提交
        # ══════════════════════════════════════════════════════════════
        print("\n正式提交並寫入 market.db 檔案 (Commit)...")
        db.session.commit()
        
        print("==================================================")
        print("Successful! 連同【號碼牌】的全系統測試資料皆已建立！")
        print("==================================================")

if __name__ == '__main__':
    seed_all_tables()