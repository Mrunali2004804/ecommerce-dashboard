# scripts/ingest_data.py
import pandas as pd
from sqlalchemy import create_engine, text
import os
from datetime import datetime

# Database Configuration
DB_CONFIG = {
    'host': 'localhost',
    'port': '5432',
    'database': 'ecommerce',
    'user': 'postgres',
    'password': 'mona@21'
}

# Create connection string
DATABASE_URL = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"

print("🔌 Connecting to PostgreSQL...")

try:
    engine = create_engine(DATABASE_URL)
    
    # Test connection
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    print("✅ Connected to PostgreSQL successfully!")

except Exception as e:
    print(f"❌ Connection failed: {e}")
    print("\n⚠️ Please make sure PostgreSQL is running and database 'ecommerce' exists.")
    print("   To create database, run in psql:")
    print("   CREATE DATABASE ecommerce;")
    exit(1)

# Step 1: Create tables
print("\n📋 Creating tables...")

CREATE_TABLES = """
-- Customers table
CREATE TABLE IF NOT EXISTS customers (
    customer_id INTEGER PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(100),
    city VARCHAR(50),
    state VARCHAR(10),
    signup_date DATE,
    is_active BOOLEAN
);

-- Products table
CREATE TABLE IF NOT EXISTS products (
    product_id INTEGER PRIMARY KEY,
    name VARCHAR(200),
    category VARCHAR(50),
    price DECIMAL(10,2),
    stock_quantity INTEGER,
    rating DECIMAL(3,1)
);

-- Orders table
CREATE TABLE IF NOT EXISTS orders (
    order_id INTEGER PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(customer_id),
    order_date TIMESTAMP,
    total_amount DECIMAL(10,2),
    status VARCHAR(20),
    num_items INTEGER
);

-- Order Items table
CREATE TABLE IF NOT EXISTS order_items (
    order_item_id INTEGER PRIMARY KEY,
    order_id INTEGER REFERENCES orders(order_id),
    product_id INTEGER REFERENCES products(product_id),
    quantity INTEGER,
    price DECIMAL(10,2),
    total DECIMAL(10,2)
);
"""

with engine.connect() as conn:
    for query in CREATE_TABLES.split(';'):
        if query.strip():
            conn.execute(text(query))
    conn.commit()
print("✅ Tables created successfully!")

# Step 2: Load data from CSV
print("\n📂 Loading data from CSV files...")

# Files to load
files = [
    ('customers', 'data/customers.csv'),
    ('products', 'data/products.csv'),
    ('orders', 'data/orders.csv'),
    ('order_items', 'data/order_items.csv')
]

for table_name, file_path in files:
    try:
        print(f"   📤 Loading {table_name}...")
        
        # Read CSV
        df = pd.read_csv(file_path)
        
        # Clean data
        df = df.replace({float('nan'): None})
        
        # Load to PostgreSQL
        df.to_sql(table_name, engine, if_exists='replace', index=False)
        
        print(f"   ✅ {len(df)} rows loaded into {table_name}")
        
    except Exception as e:
        print(f"   ❌ Error loading {table_name}: {e}")

# Step 3: Verify data
print("\n✅ Data loading complete! Verifying...")

with engine.connect() as conn:
    tables = ['customers', 'products', 'orders', 'order_items']
    for table in tables:
        result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
        count = result.scalar()
        print(f"   📊 {table}: {count} records")

print("\n🎉 DATA INGESTION COMPLETE!")
print("\n📈 You can now run analytics queries!")