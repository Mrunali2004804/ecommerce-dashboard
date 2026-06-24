# scripts/ingest_data_sqlite.py
import pandas as pd
import sqlite3
import os

DB_PATH = 'ecommerce.db'

print("🔌 Creating SQLite database...")

# Connect to SQLite (creates file if not exists)
conn = sqlite3.connect(DB_PATH)

# Drop existing tables if they exist
conn.execute("DROP TABLE IF EXISTS order_items")
conn.execute("DROP TABLE IF EXISTS orders")
conn.execute("DROP TABLE IF EXISTS products")
conn.execute("DROP TABLE IF EXISTS customers")

print("📋 Creating tables...")

# Create tables
conn.execute("""
CREATE TABLE customers (
    customer_id INTEGER PRIMARY KEY,
    name TEXT,
    email TEXT,
    city TEXT,
    state TEXT,
    signup_date DATE,
    is_active BOOLEAN
)
""")

conn.execute("""
CREATE TABLE products (
    product_id INTEGER PRIMARY KEY,
    name TEXT,
    category TEXT,
    price REAL,
    stock_quantity INTEGER,
    rating REAL
)
""")

conn.execute("""
CREATE TABLE orders (
    order_id INTEGER PRIMARY KEY,
    customer_id INTEGER,
    order_date TIMESTAMP,
    total_amount REAL,
    status TEXT,
    num_items INTEGER,
    FOREIGN KEY(customer_id) REFERENCES customers(customer_id)
)
""")

conn.execute("""
CREATE TABLE order_items (
    order_item_id INTEGER PRIMARY KEY,
    order_id INTEGER,
    product_id INTEGER,
    quantity INTEGER,
    price REAL,
    total REAL,
    FOREIGN KEY(order_id) REFERENCES orders(order_id),
    FOREIGN KEY(product_id) REFERENCES products(product_id)
)
""")

print("✅ Tables created!")

# Load CSV files
print("\n📂 Loading data from CSV files...")

files = [
    ('customers', 'data/customers.csv'),
    ('products', 'data/products.csv'),
    ('orders', 'data/orders.csv'),
    ('order_items', 'data/order_items.csv')
]

for table_name, file_path in files:
    try:
        print(f"   📤 Loading {table_name}...")
        df = pd.read_csv(file_path)
        df.to_sql(table_name, conn, if_exists='append', index=False)
        print(f"   ✅ {len(df)} rows loaded into {table_name}")
    except Exception as e:
        print(f"   ❌ Error loading {table_name}: {e}")

# Verify
print("\n📊 Data verification:")
for table in ['customers', 'products', 'orders', 'order_items']:
    cursor = conn.execute(f"SELECT COUNT(*) FROM {table}")
    count = cursor.fetchone()[0]
    print(f"   📊 {table}: {count} records")

conn.close()
print(f"\n🎉 Data loaded into {DB_PATH}!")
print("📂 Database file saved in project root!")
