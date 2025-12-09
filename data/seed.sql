
INSERT INTO customers (id, name, country) VALUES
(1, 'Alice', 'Poland'),
(2, 'Bob', 'Germany'),
(3, 'Charlie', 'Poland');

INSERT INTO products (id, name, category, price) VALUES
(1, 'Mechanical Keyboard', 'Electronics', 120.00),
(2, 'Gaming Mouse', 'Electronics', 60.00),
(3, 'Office Chair', 'Furniture', 200.00);

INSERT INTO orders (id, customer_id, order_date) VALUES
(1, 1, '2025-01-10'),
(2, 1, '2025-01-12'),
(3, 2, '2025-01-13');

INSERT INTO order_items (id, order_id, product_id, quantity, unit_price) VALUES
(1, 1, 1, 1, 120.00),
(2, 1, 2, 2, 60.00),
(3, 2, 3, 1, 200.00),
(4, 3, 2, 1, 60.00);
