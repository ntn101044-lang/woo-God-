-- 建立 Event 資料表
CREATE TABLE event (
    event_id VARCHAR(36) PRIMARY KEY,
    event_name VARCHAR(100) NOT NULL,
    start_date VARCHAR(20),
    end_date VARCHAR(20),
    map_image_url VARCHAR(255)
);

-- 建立 Vendor 資料表
CREATE TABLE vendor (
    vendor_id VARCHAR(36) PRIMARY KEY,
    account VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(50) NOT NULL,
    phone VARCHAR(20)
);

-- 建立 Visitor 資料表
CREATE TABLE visitor (
    visitor_id VARCHAR(36) PRIMARY KEY,
    account VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL
);

-- 建立 Product 資料表
CREATE TABLE product (
    product_id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    price FLOAT NOT NULL
);

-- 建立 Stall 資料表
CREATE TABLE stall (
    stall_id VARCHAR(36) PRIMARY KEY,
    stall_name VARCHAR(100) NOT NULL,
    zone_type VARCHAR(20),
    status VARCHAR(20) DEFAULT 'active',
    stall_number INTEGER UNIQUE,
    vendor_id VARCHAR(36) UNIQUE,
    event_id VARCHAR(36),
    FOREIGN KEY(vendor_id) REFERENCES vendor(vendor_id),
    FOREIGN KEY(event_id) REFERENCES event(event_id)
);

-- 建立 Offers 資料表
CREATE TABLE offers (
    stall_id VARCHAR(36),
    product_id VARCHAR(36),
    PRIMARY KEY (stall_id, product_id),
    FOREIGN KEY(stall_id) REFERENCES stall(stall_id),
    FOREIGN KEY(product_id) REFERENCES product(product_id)
);

-- 建立 QueueTicket 資料表
CREATE TABLE queue_ticket (
    ticket_id VARCHAR(36) PRIMARY KEY,
    ticket_number VARCHAR(36),
    status VARCHAR(20) DEFAULT 'waiting',
    expected_wait_time INTEGER,
    stall_id VARCHAR(36),
    visitor_id VARCHAR(36),
    FOREIGN KEY(stall_id) REFERENCES stall(stall_id),
    FOREIGN KEY(visitor_id) REFERENCES visitor(visitor_id)
);

-- 建立 Order 資料表
CREATE TABLE "order" (
    order_id VARCHAR(36) PRIMARY KEY,
    order_time VARCHAR(30),
    status VARCHAR(20) DEFAULT 'placed',
    visitor_id VARCHAR(36),
    stall_id VARCHAR(36),
    FOREIGN KEY(visitor_id) REFERENCES visitor(visitor_id),
    FOREIGN KEY(stall_id) REFERENCES stall(stall_id)
);

-- 建立 Includes 資料表
CREATE TABLE includes (
    order_id VARCHAR(36),
    product_id VARCHAR(36),
    quantity INTEGER NOT NULL DEFAULT 1,
    sold_price FLOAT NOT NULL,
    PRIMARY KEY (order_id, product_id),
    FOREIGN KEY(order_id) REFERENCES "order"(order_id),
    FOREIGN KEY(product_id) REFERENCES product(product_id)
);