# seed_jiayi.py
from app import app, db, Product, Order, Includes 
from datetime import datetime

def seed_my_tables():
    with app.app_context():
        print("開始清理舊資料，確保不重複插入...")
        # 依照外鍵相依性，先刪除子表明細
        Includes.query.delete()
        Order.query.delete()
        Product.query.delete()

        print("正在建立產品測試資料...")
        # 1. 實例化 Product 物件
        p1 = Product(name="古早味雞蛋糕", price=55.0)
        p2 = Product(name="起司雞蛋糕", price=65.0)
        p3 = Product(name="黑糖珍珠鮮奶", price=70.0)
        
        db.session.add_all([p1, p2, p3])
        db.session.flush()  # 獲取自動生成的 UUID

        print("正在建立測試訂單資料...")
        # 2. 實例化 Order 物件
        o1 = Order(
            order_time=datetime.now().strftime("%Y-%m-%d %H:%M"),
            status="placed" 
        )
        o2 = Order(
            order_time=datetime.now().strftime("%Y-%m-%d %H:%M"),
            status="placed"
        )
        
        db.session.add_all([o1, o2])
        db.session.flush()

        print("將資料放入資料庫快取區 (建立 Includes 關聯)...")
        # 3. 建立關聯明細並加入 session
        inc1 = Includes(order_id=o1.order_id, product_id=p2.product_id, quantity=2, sold_price=p2.price)
        inc2 = Includes(order_id=o2.order_id, product_id=p1.product_id, quantity=1, sold_price=p1.price)
        inc3 = Includes(order_id=o2.order_id, product_id=p3.product_id, quantity=1, sold_price=p3.price)

        db.session.add_all([inc1, inc2, inc3])

        print("正式提交並寫入檔案 (Commit)...")
        # 4. 正式寫入 market.db 檔案中
        db.session.commit()
        print("Successful!")

if __name__ == '__main__':
    seed_my_tables()