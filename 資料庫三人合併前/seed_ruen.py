# seed_ruen.py
from app import app, db, Event, Visitor, Vendor, Stall, Product, offers
from datetime import datetime

def seed_my_tables():
    with app.app_context():
        print("【第三防區】開始清理舊資料...")
        # 💡 修正 1：因為 offers 是 db.Table，要用 db.session.execute 清理
        db.session.execute(offers.delete())
        Stall.query.delete()
        Vendor.query.delete()

        print("正在建立測試攤商資料 (Vendor)...")
        # 💡 修正 2：欄位名稱改為小寫，並補上 app.py 要求的 account 與密碼
        vendor_1 = Vendor(
            account="fanyu@example.com",  # 補上必填的帳號
            name="芳妤網美雞蛋糕",
            phone="0912345678"
        )
        vendor_1.set_password("fanyu123") # 呼叫 app.py 的密碼加密功能
        db.session.add(vendor_1)
        db.session.flush() # 讓系統先幫 vendor_1 生成 UUID vendor_id

        print("正在抓取偉詠建立的市集活動...")
        target_event = Event.query.first()
        current_event_id = target_event.event_id if target_event else None

        print("正在建立測試攤位資料 (Stall)...")
        # 💡 修正 3：欄位名稱改為小寫對齊 app.py
        stall_1 = Stall(
            stall_name="雞蛋糕 A 攤",
            zone_type="美食區",
            status="綠燈", 
            event_id=current_event_id,
            vendor_id=vendor_1.vendor_id  # 🔗 自動帶入剛剛產生的 UUID
        )
        db.session.add(stall_1)
        db.session.flush() # 讓系統幫 stall_1 生成 UUID stall_id

        print("正在建立攤位商品交集資料 (Offers)...")
        # 💡 修正 4：符合 app.py 的多對多寫法，直接用 .append 把商品塞進去
        # 我們先暫時建立一個測試商品 ProductID = 101 (或由商品防區提供)
        test_product = Product(name="測試雞蛋糕品項", price=60.0)
        db.session.add(test_product)
        db.session.flush()

        # 這樣寫，Flask-SQLAlchemy 就會全自動幫你寫入 offers 那張多對多表！
        stall_1.products.append(test_product)

        print("正式將【第三防區】所有資料提交 (Commit)...")
        db.session.commit()
        print("Successful! 如恩防區的限制式驗證與測試資料皆建立完成！")

if __name__ == '__main__':
    seed_my_tables()