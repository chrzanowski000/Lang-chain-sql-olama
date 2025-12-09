# Tables

## customers
- id (integer) - primary key
- name (text)
- country (text)

## products
- id (integer) - primary key
- name (text)
- category (text)
- price (numeric)

## orders
- id (integer) - primary key
- customer_id (integer) - FK -> customers.id
- order_date (text) - YYYY-MM-DD

## order_items
- id (integer) - primary key
- order_id (integer) - FK -> orders.id
- product_id (integer) - FK -> products.id
- quantity (integer)
- unit_price (numeric)
