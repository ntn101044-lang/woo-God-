# seed_jiayi_ruen_weiyong.py 
from app import app, db, Event, Visitor, Vendor, Stall, Product, QueueTicket, Order, Includes, offers
from datetime import datetime

def seed_all_tables():
    with app.app_context():
        print("==================================================")
        print("【全系統初始化】開始清理舊資料，確保不重複插入...")
        print("==================================================")
        
        # ⚠️ 統一清理所有資料表 (包含家億防區的 Order 與 Includes)
        Includes.query.delete()
        Order.query.delete()
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
        print("\n[1/5] 正在建立活動與遊客資料...")
        target_event = Event(
            event_name="華山文創夏日風格市集",
            start_date="2026-07-10",
            end_date="2026-07-15",
            map_image_url="https://images.example.com/huashan_map.jpg"
        )
        db.session.add(target_event)
        
        # 🎯 修改這裡：對齊前端 index.html 的遊客測試帳密
        visitor_1 = Visitor(account="user01@example.com")
        visitor_1.set_password("password123")
        
        visitor_2 = Visitor(account="taipei_user02@example.com")
        visitor_2.set_password("hello2026")
        
        db.session.add(visitor_1)
        db.session.add(visitor_2)
        db.session.flush() 

        # ══════════════════════════════════════════════════════════════
        # 2. 如恩的防區：建立泰式奶茶攤位
        # ══════════════════════════════════════════════════════════════
        print("\n[2/5] 正在建立如恩泰式奶茶攤位...")
        
        # 🎯 修改這裡：對齊前端 index.html 的攤主測試帳密
        vendor_1 = Vendor(
            account="vendor1",
            name="如恩正宗泰式奶茶",
            phone="0988777666"
        )
        vendor_1.set_password("1234") 
        db.session.add(vendor_1)
        db.session.flush()

        stall_1 = Stall(
            stall_name="如恩泰奶 01 號攤",
            zone_type="Drinks",
            status="active",
            event_id=target_event.event_id,
            vendor_id=vendor_1.vendor_id
        )
        db.session.add(stall_1)
        db.session.flush()

        # ══════════════════════════════════════════════════════════════
        # 3. 商品與上架功能測試
        # ══════════════════════════════════════════════════════════════
        print("\n[3/5] 正在上架泰奶菜單...")
        product_1 = Product(name="手標正宗泰式奶茶", price=70.0)
        db.session.add(product_1)
        db.session.flush()
        stall_1.products.append(product_1)

        # ══════════════════════════════════════════════════════════════
        # 4. 模擬遊客來「抽號碼牌 (QueueTicket)」
        # ══════════════════════════════════════════════════════════════
        print("\n[4/5] 🚀 正在模擬遊客線上抽號碼牌...")
        ticket_1 = QueueTicket(
            ticket_number="1",
            status="waiting",
            expected_wait_time=15,
            stall_id=stall_1.stall_id,
            visitor_id=visitor_1.visitor_id
        )
        ticket_2 = QueueTicket(
            ticket_number="2",
            status="waiting",
            expected_wait_time=30,
            stall_id=stall_1.stall_id,
            visitor_id=visitor_2.visitor_id
        )
        db.session.add(ticket_1)
        db.session.add(ticket_2)

        # ══════════════════════════════════════════════════════════════
        # 5. 🔥 家億的防區：產品、訂單與明細關聯
        # ══════════════════════════════════════════════════════════════
        print("\n[5/5] 正在導入家億防區資料 (產品、訂單、明細)...")
        
        # 1. 建立產品
        jiayi_p1 = Product(name="古早味雞蛋糕", price=55.0)
        jiayi_p2 = Product(name="起司雞蛋糕", price=65.0)
        jiayi_p3 = Product(name="黑糖珍珠鮮奶", price=70.0)
        db.session.add_all([jiayi_p1, jiayi_p2, jiayi_p3])
        db.session.flush()

        # 2. 建立訂單
        jiayi_o1 = Order(order_time=datetime.now().strftime("%Y-%m-%d %H:%M"), status="placed", visitor_id=visitor_1.visitor_id, stall_id=stall_1.stall_id)
        jiayi_o2 = Order(order_time=datetime.now().strftime("%Y-%m-%d %H:%M"), status="placed", visitor_id=visitor_1.visitor_id, stall_id=stall_1.stall_id)
        db.session.add_all([jiayi_o1, jiayi_o2])
        db.session.flush()

        # 3. 建立關聯明細
        jiayi_inc1 = Includes(order_id=jiayi_o1.order_id, product_id=jiayi_p2.product_id, quantity=2, sold_price=jiayi_p2.price)
        jiayi_inc2 = Includes(order_id=jiayi_o2.order_id, product_id=jiayi_p1.product_id, quantity=1, sold_price=jiayi_p1.price)
        jiayi_inc3 = Includes(order_id=jiayi_o2.order_id, product_id=jiayi_p3.product_id, quantity=1, sold_price=jiayi_p3.price)
        db.session.add_all([jiayi_inc1, jiayi_inc2, jiayi_inc3])

        # ══════════════════════════════════════════════════════════════
        # 6. 正式提交
        # ══════════════════════════════════════════════════════════════
        print("\n正式提交並寫入 market.db 檔案 (Commit)...")
        db.session.commit()
        
        print("==================================================")
        print("Successful! 全系統資料已建立！")
        print("==================================================")

if __name__ == '__main__':
    seed_all_tables()