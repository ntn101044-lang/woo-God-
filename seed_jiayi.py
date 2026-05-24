# seed_jiayi.py
from app import db, Product, Order, Includes 
from datetime import datetime

def seed_jiayi_data():
    print("正在建立家億防區：產品與訂單資料...")
    
    # 1. 建立產品資料
    p1 = Product(name="古早味雞蛋糕", price=55.0)
    p2 = Product(name="起司雞蛋糕", price=65.0)
    p3 = Product(name="黑糖珍珠鮮奶", price=70.0)
    db.session.add_all([p1, p2, p3])
    db.session.flush() 

    # 2. 建立訂單資料
    o1 = Order(order_time=datetime.now().strftime("%Y-%m-%d %H:%M"), status="placed")
    o2 = Order(order_time=datetime.now().strftime("%Y-%m-%d %H:%M"), status="placed")
    db.session.add_all([o1, o2])
    db.session.flush()

    # 3. 建立關聯明細
    inc1 = Includes(order_id=o1.order_id, product_id=p2.product_id, quantity=2, sold_price=p2.price)
    inc2 = Includes(order_id=o2.order_id, product_id=p1.product_id, quantity=1, sold_price=p1.price)
    inc3 = Includes(order_id=o2.order_id, product_id=p3.product_id, quantity=1, sold_price=p3.price)
    db.session.add_all([inc1, inc2, inc3])

if __name__ == '__main__':
    from app import app
    with app.app_context():
        # 自己跑的時候才執行刪除
        Includes.query.delete()
        Order.query.delete()
        Product.query.delete()
        seed_jiayi_data()
        db.session.commit()
        print("Successful! 家億測試資料已建立。")