# seed_jiayi_ruen_weiyong.py 
from app import app, db, Event, Visitor, Vendor, Stall, Product, QueueTicket, Order, Includes, offers
from datetime import datetime

def seed_all_tables():
    with app.app_context():
        print("==================================================")
        print("【全系統初始化】開始清理舊資料，確保不重複插入...")
        print("==================================================")
        
        # 統一清理所有資料表 (包含家億防區的 Order 與 Includes)
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
        # 1.建立市集活動與遊客 (Event & Visitor)
        # ══════════════════════════════════════════════════════════════
        print("\n[1/5] Event and visitor data are being established...")
        target_event = Event(
            event_name="Summer-themed market",
            start_date="2026-05-10",
            end_date="2026-06-20",
            map_image_url="https://images.example.com/huashan_map.jpg"
        )
        db.session.add(target_event)
    
        visitor_1 = Visitor(account="user01@example.com")
        visitor_1.set_password("password123")
        
        visitor_2 = Visitor(account="taipei_user02@example.com")
        visitor_2.set_password("hello2026")
        
        db.session.add(visitor_1)
        db.session.add(visitor_2)
        db.session.flush() 

        # ══════════════════════════════════════════════════════════════
        # 2. 建立攤位與攤主資訊
        # ══════════════════════════════════════════════════════════════
        print("\n[2/5] Thai milk tea stalls are being set up...")
        vendor_1 = Vendor(
            account="vendor1",
            name="Thai milk tea",
            phone="0988777666"
        )
        vendor_1.set_password("1234") 
        db.session.add(vendor_1)
        db.session.flush()

        stall_1 = Stall(
            stall_name="Thai milk tea",
            zone_type="drink",
            status="active",
            event_id=target_event.event_id,
            vendor_id=vendor_1.vendor_id
        )
        db.session.add(stall_1)
        db.session.flush()

        vendor_2 = Vendor(
        account="vendor2",
        name="Grandma's Chicken Cake",
        phone="0911222333"
        )
        vendor_2.set_password("1234")
        db.session.add(vendor_2)
        db.session.flush()

        stall_2 = Stall(
            stall_name="Grandma's Chicken Cake",
            zone_type="food",
            status="active",
            event_id=target_event.event_id,
            vendor_id=vendor_2.vendor_id
        )

        db.session.add(stall_2)
        db.session.flush()


        # ═════════════ Food ═════════════

        vendor_3 = Vendor(
            account="vendor3",
            name="Grilled Steak House",
            phone="0922333444"
        )
        vendor_3.set_password("1234")
        db.session.add(vendor_3)
        db.session.flush()

        stall_3 = Stall(
            stall_name="Grilled Steak House",
            zone_type="food",
            status="active",
            event_id=target_event.event_id,
            vendor_id=vendor_3.vendor_id
        )

        db.session.add(stall_3)
        db.session.flush()


        # ═════════════ Drink ═════════════

        vendor_4 = Vendor(
            account="vendor4",
            name="fresh juice",
            phone="0933444555"
        )
        vendor_4.set_password("1234")
        db.session.add(vendor_4)
        db.session.flush()

        stall_4 = Stall(
            stall_name="fresh juice",
            zone_type="drink",
            status="active",
            event_id=target_event.event_id,
            vendor_id=vendor_4.vendor_id
        )

        db.session.add(stall_4)
        db.session.flush()


        # ═════════════ Drink ═════════════

        vendor_5 = Vendor(
            account="vendor5",
            name="sunset coffee",
            phone="0944555666"
        )
        vendor_5.set_password("1234")
        db.session.add(vendor_5)
        db.session.flush()

        stall_5 = Stall(
            stall_name="sunset coffee",
            zone_type="drink",
            status="active",
            event_id=target_event.event_id,
            vendor_id=vendor_5.vendor_id
        )

        db.session.add(stall_5)
        db.session.flush()


        # ═════════════ Craft ═════════════

        vendor_6 = Vendor(
            account="vendor6",
            name="Mumu Handmade Workshop",
            phone="0955666777"
        )
        vendor_6.set_password("1234")
        db.session.add(vendor_6)
        db.session.flush()

        stall_6 = Stall(
            stall_name="Mumu Handmade Workshop",
            zone_type="craft",
            status="active",
            event_id=target_event.event_id,
            vendor_id=vendor_6.vendor_id
        )

        db.session.add(stall_6)
        db.session.flush()


        # ═════════════ Craft ═════════════

        vendor_7 = Vendor(
            account="vendor7",
            name="Weaving time",
            phone="0966777888"
        )
        vendor_7.set_password("1234")
        db.session.add(vendor_7)
        db.session.flush()

        stall_7 = Stall(
            stall_name="Weaving time",
            zone_type="craft",
            status="active",
            event_id=target_event.event_id,
            vendor_id=vendor_7.vendor_id
        )

        db.session.add(stall_7)
        db.session.flush()

        # ══════════════════════════════════════════════════════════════
        # 3. 商品與上架功能測試
        # ══════════════════════════════════════════════════════════════
        # ═════════════ Thai milk tea ═════════════

        thai_1 = Product(name="Hand-branded authentic Thai milk tea", price=70.0)
        thai_2 = Product(name="Thai Green Milk Tea", price=75.0)
        thai_3 = Product(name="Thai Lemon Tea", price=65.0)

        db.session.add_all([thai_1, thai_2, thai_3])
        db.session.flush()

        stall_1.products.extend([thai_1, thai_2, thai_3])


        # ═════════════ 阿嬤古早味雞蛋糕 ═════════════

        cake_1 = Product(name="Original Egg Cake", price=55.0)
        cake_2 = Product(name="Cheese Egg Cake", price=65.0)
        cake_3 = Product(name="Chocolate Egg Cake", price=70.0)

        db.session.add_all([cake_1, cake_2, cake_3])
        db.session.flush()

        stall_2.products.extend([cake_1, cake_2, cake_3])


        # ═════════════ 炙燒牛排小屋 ═════════════

        steak_1 = Product(name="Sirloin Steak", price=180.0)
        steak_2 = Product(name="Chicken Steak", price=150.0)
        steak_3 = Product(name="Double Cheese Steak", price=220.0)

        db.session.add_all([steak_1, steak_2, steak_3])
        db.session.flush()

        stall_3.products.extend([steak_1, steak_2, steak_3])


        # ═════════════ 鮮果汁 ═════════════

        juice_1 = Product(name="Watermelon Juice", price=60.0)
        juice_2 = Product(name="Orange Juice", price=65.0)
        juice_3 = Product(name="Mixed Fruit Juice", price=80.0)

        db.session.add_all([juice_1, juice_2, juice_3])
        db.session.flush()

        stall_4.products.extend([juice_1, juice_2, juice_3])


        # ═════════════ 日落咖啡 ═════════════

        coffee_1 = Product(name="Americano", price=80.0)
        coffee_2 = Product(name="Latte", price=100.0)
        coffee_3 = Product(name="Caramel Latte", price=120.0)

        db.session.add_all([coffee_1, coffee_2, coffee_3])
        db.session.flush()

        stall_5.products.extend([coffee_1, coffee_2, coffee_3])


        # ═════════════ 木木手作工坊 ═════════════

        craft_1 = Product(name="Handmade Wooden Coaster", price=150.0)
        craft_2 = Product(name="Wooden Keychain", price=120.0)
        craft_3 = Product(name="Mini Wooden Decoration", price=180.0)

        db.session.add_all([craft_1, craft_2, craft_3])
        db.session.flush()

        stall_6.products.extend([craft_1, craft_2, craft_3])


        # ═════════════ 編織時光 ═════════════

        weave_1 = Product(name="Handmade Bracelet", price=100.0)
        weave_2 = Product(name="Woven Coin Purse", price=250.0)
        weave_3 = Product(name="Handmade Tote Bag", price=450.0)

        db.session.add_all([weave_1, weave_2, weave_3])
        db.session.flush()

        stall_7.products.extend([weave_1, weave_2, weave_3])


        # ══════════════════════════════════════════════════════════════
        # 4. (QueueTicket)&假的排隊資料」
        # ══════════════════════════════════════════════════════════════
        for i in range(1, 31):
            ticket = QueueTicket(
                ticket_number=str(i),
                status="waiting",
                expected_wait_time=i * 3,
                stall_id=stall_1.stall_id,
                visitor_id=visitor_1.visitor_id
            )
            db.session.add(ticket)

        # 阿嬤古早味雞蛋糕：12人
        for i in range(1, 13):
            db.session.add(
                QueueTicket(
                    ticket_number=str(i),
                    status="waiting",
                    expected_wait_time=i * 3,
                    stall_id=stall_2.stall_id,
                    visitor_id=visitor_1.visitor_id
                )
            )

        # 炙燒牛排小屋：9人
        for i in range(1, 10):
            db.session.add(
                QueueTicket(
                    ticket_number=str(i),
                    status="waiting",
                    expected_wait_time=i * 3,
                    stall_id=stall_3.stall_id,
                    visitor_id=visitor_1.visitor_id
                )
            )

        # 果然鮮果汁：7人
        for i in range(1, 8):
            db.session.add(
                QueueTicket(
                    ticket_number=str(i),
                    status="waiting",
                    expected_wait_time=i * 3,
                    stall_id=stall_4.stall_id,
                    visitor_id=visitor_1.visitor_id
                )
            )

        # 日落咖啡：5人
        for i in range(1, 6):
            db.session.add(
                QueueTicket(
                    ticket_number=str(i),
                    status="waiting",
                    expected_wait_time=i * 3,
                    stall_id=stall_5.stall_id,
                    visitor_id=visitor_2.visitor_id
                )
            )

        # 木木手作工坊：3人
        for i in range(1, 4):
            db.session.add(
                QueueTicket(
                    ticket_number=str(i),
                    status="waiting",
                    expected_wait_time=i * 3,
                    stall_id=stall_6.stall_id,
                    visitor_id=visitor_2.visitor_id
                )
            )

        # 編織時光：1人
        for i in range(1, 2):
            db.session.add(
                QueueTicket(
                    ticket_number=str(i),
                    status="waiting",
                    expected_wait_time=i * 3,
                    stall_id=stall_7.stall_id,
                    visitor_id=visitor_2.visitor_id
                )
            )

        # ══════════════════════════════════════════════════════════════
        # 5. 正式提交
        # ══════════════════════════════════════════════════════════════
        print("\nFormal submission (Commit)...")
        db.session.commit()
        
        print("==================================================")
        print("Successful! 全系統資料已建立！")
        print("==================================================")

if __name__ == '__main__':
    seed_all_tables()