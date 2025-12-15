
set -euo pipefail
mkdir -p data_csv
DB=${1:-./shop.db}

sqlite3 "$DB" -header -csv "SELECT * FROM products;"  > data_csv/products.csv
sqlite3 "$DB" -header -csv "SELECT * FROM customers;" > data_csv/customers.csv
sqlite3 "$DB" -header -csv "SELECT * FROM orders;"    > data_csv/orders.csv
sqlite3 "$DB" -header -csv "SELECT * FROM order_items;" > data_csv/order_items.csv

echo "Exported CSVs to data/"
