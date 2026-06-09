-- ------------------------------------------------------------------------------
-- 查詢一：熱門攤位即時排隊人數統計 (涵蓋 LEFT JOIN, COUNT, GROUP BY, ORDER BY)
-- 說明：用於系統首頁，計算每個攤位目前「正在等待 (waiting)」的號碼牌數量，
--       並由多到少排序，藉此向遊客推薦熱門攤位。
-- ------------------------------------------------------------------------------
SELECT 
    s.stall_id, 
    s.stall_name, 
    COUNT(q.ticket_id) AS waiting_people
FROM stall s
LEFT JOIN queue_ticket q 
    ON s.stall_id = q.stall_id AND q.status = 'waiting'
WHERE s.status = 'active'
GROUP BY s.stall_id, s.stall_name
ORDER BY waiting_people DESC;


-- ------------------------------------------------------------------------------
-- 查詢二：訂單完整明細查詢 (涵蓋 跨四張表的 INNER JOIN, 算術運算)
-- 說明：用於攤商後台。當攤商點開某筆特定訂單時，系統需跨表抓取遊客帳號、
--       購買的商品名稱、數量與單價，並直接在資料庫端算出小計 (Subtotal)。
-- ------------------------------------------------------------------------------
SELECT 
    o.order_id, 
    v.account AS buyer_account, 
    p.name AS product_name, 
    i.quantity, 
    i.sold_price, 
    (i.quantity * i.sold_price) AS subtotal
FROM "order" o
JOIN visitor v 
    ON o.visitor_id = v.visitor_id
JOIN includes i 
    ON o.order_id = i.order_id
JOIN product p 
    ON i.product_id = p.product_id
WHERE o.order_id = '替換成實際的訂單ID'; -- 實際執行時替換為欲查詢的 order_id


-- ------------------------------------------------------------------------------
-- 查詢三：異常壅塞攤位警示 (涵蓋 Subquery 子查詢, HAVING, AVG)
-- 說明：進階商業邏輯分析。利用子查詢先算出「全市場整體的平均等待時間」，
--       再篩選出「自身平均等待時間」大於「全市場平均」的壅塞攤位。
-- ------------------------------------------------------------------------------
SELECT 
    s.stall_name, 
    AVG(q.expected_wait_time) AS avg_stall_wait_time
FROM stall s
JOIN queue_ticket q 
    ON s.stall_id = q.stall_id
WHERE q.status = 'waiting'
GROUP BY s.stall_id, s.stall_name
HAVING AVG(q.expected_wait_time) > (
    -- 子查詢：計算全市場所有 waiting 號碼牌的平均等待時間
    SELECT AVG(expected_wait_time) 
    FROM queue_ticket 
    WHERE status = 'waiting'
);


-- ------------------------------------------------------------------------------
-- 查詢四：高消費 VIP 遊客分析 (涵蓋 JOIN, GROUP BY, SUM, HAVING)
-- 說明：列出在市集中累積消費總額超過 500 元的遊客帳號及其總花費，
--       可作為未來市集發放優惠券或 VIP 行銷的依據。
-- ------------------------------------------------------------------------------
SELECT 
    v.account, 
    SUM(i.quantity * i.sold_price) AS total_spent
FROM visitor v
JOIN "order" o 
    ON v.visitor_id = o.visitor_id
JOIN includes i 
    ON o.order_id = i.order_id
GROUP BY v.visitor_id, v.account
HAVING SUM(i.quantity * i.sold_price) > 500
ORDER BY total_spent DESC;