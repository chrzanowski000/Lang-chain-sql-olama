
INSERT INTO customers (id, name, country) VALUES
(4, 'Diana', 'France'),
(5, 'Ethan', 'USA'),
(6, 'Fiona', 'UK'),
(7, 'George', 'Canada'),
(8, 'Hannah', 'Sweden'),
(9, 'Ivan', 'Poland'),
(10, 'Julia', 'Germany');


INSERT INTO products (id, name, category, price) VALUES
(4, 'Standing Desk', 'Furniture', 350.00),
(5, 'USB-C Hub', 'Electronics', 45.00),
(6, 'Noise-Cancelling Headphones', 'Electronics', 180.00),
(7, 'LED Monitor 27"', 'Electronics', 300.00),
(8, 'Ergonomic Mousepad', 'Accessories', 25.00),
(9, 'Laptop Stand', 'Accessories', 40.00),
(10, 'Bookshelf', 'Furniture', 150.00);


INSERT INTO orders (id, customer_id, order_date) VALUES
(4, 3, '2025-01-15'),
(5, 4, '2025-01-16'),
(6, 5, '2025-01-17'),
(7, 6, '2025-01-17'),
(8, 7, '2025-01-18'),
(9, 8, '2025-01-18'),
(10, 9, '2025-01-19'),
(11, 10, '2025-01-20');


INSERT INTO order_items (id, order_id, product_id, quantity, unit_price) VALUES
-- Order 4 (Charlie)
(5, 4, 6, 1, 180.00),
(6, 4, 5, 2, 45.00),

-- Order 5 (Diana)
(7, 5, 7, 1, 300.00),
(8, 5, 8, 1, 25.00),

-- Order 6 (Ethan)
(9, 6, 4, 1, 350.00),
(10, 6, 9, 1, 40.00),

-- Order 7 (Fiona)
(11, 7, 6, 1, 180.00),
(12, 7, 2, 1, 60.00),

-- Order 8 (George)
(13, 8, 1, 1, 120.00),
(14, 8, 10, 1, 150.00),

-- Order 9 (Hannah)
(15, 9, 7, 1, 300.00),

-- Order 10 (Ivan)
(16, 10, 5, 3, 45.00),
(17, 10, 8, 2, 25.00),

-- Order 11 (Julia)
(18, 11, 3, 1, 200.00),
(19, 11, 9, 1, 40.00);
