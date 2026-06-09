-- =========================================================
-- 1. 建立市集活動 (Event)
-- =========================================================
INSERT INTO event (event_id, event_name, start_date, end_date, map_image_url) 
VALUES ('evt_01', 'Summer-themed market', '2026-05-10', '2026-06-20', 'https://images.example.com/huashan_map.jpg');

-- =========================================================
-- 2. 建立遊客 (Visitor)
-- =========================================================
-- 密碼欄位以假 hash 字串示意，以符合系統結構
INSERT INTO visitor (visitor_id, account, password_hash) 
VALUES 
('vis_01', 'user01@example.com', 'pbkdf2:sha256:hashed_pw_1'),
('vis_02', 'taipei_user02@example.com', 'pbkdf2:sha256:hashed_pw_2');

-- =========================================================
-- 3. 建立攤商 (Vendor)
-- =========================================================
INSERT INTO vendor (vendor_id, account, password_hash, name, phone) 
VALUES 
('ven_01', 'vendor1', 'hash1', 'Thai milk tea', '0988777666'),
('ven_02', 'vendor2', 'hash2', 'Grandma''s Chicken Cake', '0911222333'),
('ven_03', 'vendor3', 'hash3', 'Grilled Steak House', '0922333444'),
('ven_04', 'vendor4', 'hash4', 'fresh juice', '0933444555'),
('ven_05', 'vendor5', 'hash5', 'sunset coffee', '0944555666'),
('ven_06', 'vendor6', 'hash6', 'Mumu Handmade Workshop', '0955666777'),
('ven_07', 'vendor7', 'hash7', 'Weaving time', '0966777888');

-- =========================================================
-- 4. 建立攤位 (Stall)
-- =========================================================
INSERT INTO stall (stall_id, stall_name, zone_type, status, stall_number, vendor_id, event_id) 
VALUES 
('stl_01', 'Thai milk tea', 'drink', 'active', 1, 'ven_01', 'evt_01'),
('stl_02', 'Grandma''s Chicken Cake', 'food', 'active', 2, 'ven_02', 'evt_01'),
('stl_03', 'Grilled Steak House', 'food', 'active', 3, 'ven_03', 'evt_01'),
('stl_04', 'fresh juice', 'drink', 'active', 4, 'ven_04', 'evt_01'),
('stl_05', 'sunset coffee', 'drink', 'active', 5, 'ven_05', 'evt_01'),
('stl_06', 'Mumu Handmade Workshop', 'craft', 'active', 6, 'ven_06', 'evt_01'),
('stl_07', 'Weaving time', 'craft', 'active', 7, 'ven_07', 'evt_01');

-- =========================================================
-- 5. 建立商品 (Product) 
-- =========================================================
INSERT INTO product (product_id, name, price) 
VALUES 
-- Thai milk tea
('p_1_1', 'Hand-branded authentic Thai milk tea', 70.0),
('p_1_2', 'Thai Green Milk Tea', 75.0),
('p_1_3', 'Thai Lemon Tea', 65.0),
-- Grandma's Chicken Cake
('p_2_1', 'Original Egg Cake', 55.0),
('p_2_2', 'Cheese Egg Cake', 65.0),
('p_2_3', 'Chocolate Egg Cake', 70.0),
-- Grilled Steak House
('p_3_1', 'Sirloin Steak', 180.0),
('p_3_2', 'Chicken Steak', 150.0),
('p_3_3', 'Double Cheese Steak', 220.0),
-- fresh juice
('p_4_1', 'Watermelon Juice', 60.0),
('p_4_2', 'Orange Juice', 65.0),
('p_4_3', 'Mixed Fruit Juice', 80.0),
-- sunset coffee
('p_5_1', 'Americano', 80.0),
('p_5_2', 'Latte', 100.0),
('p_5_3', 'Caramel Latte', 120.0),
-- Mumu Handmade Workshop
('p_6_1', 'Handmade Wooden Coaster', 150.0),
('p_6_2', 'Wooden Keychain', 120.0),
('p_6_3', 'Mini Wooden Decoration', 180.0),
-- Weaving time
('p_7_1', 'Handmade Bracelet', 100.0),
('p_7_2', 'Woven Coin Purse', 250.0),
('p_7_3', 'Handmade Tote Bag', 450.0);

-- =========================================================
-- 6. 建立攤位與商品對應 (Offers)
-- =========================================================
INSERT INTO offers (stall_id, product_id) 
VALUES 
('stl_01', 'p_1_1'), ('stl_01', 'p_1_2'), ('stl_01', 'p_1_3'),
('stl_02', 'p_2_1'), ('stl_02', 'p_2_2'), ('stl_02', 'p_2_3'),
('stl_03', 'p_3_1'), ('stl_03', 'p_3_2'), ('stl_03', 'p_3_3'),
('stl_04', 'p_4_1'), ('stl_04', 'p_4_2'), ('stl_04', 'p_4_3'),
('stl_05', 'p_5_1'), ('stl_05', 'p_5_2'), ('stl_05', 'p_5_3'),
('stl_06', 'p_6_1'), ('stl_06', 'p_6_2'), ('stl_06', 'p_6_3'),
('stl_07', 'p_7_1'), ('stl_07', 'p_7_2'), ('stl_07', 'p_7_3');

-- =========================================================
-- 7. 建立號碼牌 (QueueTicket) - 提供足以測試系統的樣本
-- =========================================================
INSERT INTO queue_ticket (ticket_id, ticket_number, status, expected_wait_time, stall_id, visitor_id) 
VALUES 
-- 攤位 1 號碼牌樣本 (模擬熱門排隊狀況)
('t_1_1', '1', 'waiting', 3, 'stl_01', 'vis_01'),
('t_1_2', '2', 'waiting', 6, 'stl_01', 'vis_01'),
('t_1_3', '3', 'waiting', 9, 'stl_01', 'vis_02'),
-- 攤位 2 號碼牌樣本
('t_2_1', '1', 'waiting', 3, 'stl_02', 'vis_01'),
('t_2_2', '2', 'waiting', 6, 'stl_02', 'vis_01'),
-- 攤位 3 號碼牌樣本
('t_3_1', '1', 'waiting', 3, 'stl_03', 'vis_01'),
('t_3_2', '2', 'completed', 0, 'stl_03', 'vis_01');