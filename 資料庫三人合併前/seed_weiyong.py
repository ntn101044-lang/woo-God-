# seed_weiyong.py
from app import app, db, Event, Visitor

def seed_my_tables():
    with app.app_context():
        print("開始清理舊資料，確保不重複插入...")
        Event.query.delete()
        Visitor.query.delete()

        print("正在建立市集活動測試資料...")
        # 1. 實例化一個 Event 物件 (對應你的 Event 表)
        target_event = Event(
            event_name="高雄駁二文創智慧市集",
            start_date="2026-06-01",
            end_date="2026-06-05",
            map_image_url="https://images.example.com/pier2_map.jpg"
        )

        print("正在建立測試遊客資料...")
        # 2. 實例化兩個 Visitor 物件 (對應你的 Visitor 表)
        visitor_1 = Visitor(account="user01@example.com")
        visitor_1.set_password("password123") # 使用 app.py 裡的雜湊加密密碼

        visitor_2 = Visitor(account="user02@example.com")
        visitor_2.set_password("password456")

        print("將資料放入資料庫快取區...")
        # 3. 使用 db.session.add 將物件加入追蹤清單
        db.session.add(target_event)
        db.session.add(visitor_1)
        db.session.add(visitor_2)

        print("正式提交並寫入檔案 (Commit)...")
        # 4. 正式寫入 market.db 檔案中
        db.session.commit()
        print("Successful!")

if __name__ == '__main__':
    seed_my_tables()
