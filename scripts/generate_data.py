# scripts/generate_data.py
import pandas as pd
import numpy as np
from faker import Faker
import random
from datetime import datetime, timedelta
import os

# Ensure data directory exists
os.makedirs('data', exist_ok=True)

fake = Faker()
Faker.seed(42)
random.seed(42)
np.random.seed(42)

# Configuration - Test ke liye chhota data
NUM_CUSTOMERS = 1000
NUM_PRODUCTS = 100
NUM_ORDERS = 5000
START_DATE = datetime(2025, 1, 1)
END_DATE = datetime(2026, 6, 24)

print("🔄 Generating mock data...")

# 1. Generate Customers
print("📋 Generating customers...")
customers = []
for i in range(NUM_CUSTOMERS):
    customers.append({
        'customer_id': i + 1,
        'name': fake.name(),
        'email': fake.email(),
        'city': fake.city(),
        'state': fake.state_abbr(),
        'signup_date': fake.date_between(start_date=START_DATE, end_date=END_DATE),
        'is_active': random.choice([True, False])
    })
df_customers = pd.DataFrame(customers)
df_customers.to_csv('data/customers.csv', index=False)
print(f"✅ {NUM_CUSTOMERS} customers created!")

# 2. Generate Products
print("📦 Generating products...")
categories = ['Electronics', 'Clothing', 'Books', 'Home & Garden', 'Sports', 'Toys', 'Automotive']
products = []
for i in range(NUM_PRODUCTS):
    products.append({
        'product_id': i + 1,
        'name': fake.catch_phrase(),
        'category': random.choice(categories),
        'price': round(random.uniform(5.99, 999.99), 2),
        'stock_quantity': random.randint(0, 500),
        'rating': round(random.uniform(1.0, 5.0), 1)
    })
df_products = pd.DataFrame(products)
df_products.to_csv('data/products.csv', index=False)
print(f"✅ {NUM_PRODUCTS} products created!")

# 3. Generate Orders
print("🛒 Generating orders...")
orders = []
order_statuses = ['Pending', 'Processing', 'Shipped', 'Delivered', 'Cancelled']

for i in range(NUM_ORDERS):
    customer_id = random.randint(1, NUM_CUSTOMERS)
    num_items = random.randint(1, 5)
    
    order_date = fake.date_time_between(start_date=START_DATE, end_date=END_DATE)
    status = random.choice(order_statuses)
    
    total_amount = 0
    for _ in range(num_items):
        price = random.uniform(5.99, 999.99)
        total_amount += price * random.randint(1, 3)
    
    orders.append({
        'order_id': i + 1,
        'customer_id': customer_id,
        'order_date': order_date,
        'total_amount': round(total_amount, 2),
        'status': status,
        'num_items': num_items
    })
    
    if (i + 1) % 1000 == 0:
        print(f"   ✅ {i+1} orders generated...")

df_orders = pd.DataFrame(orders)
df_orders.to_csv('data/orders.csv', index=False)
print(f"✅ {NUM_ORDERS} orders created!")

# 4. Generate Order Items
print("📝 Generating order items...")
order_items = []
item_id = 1

for order_id in range(1, NUM_ORDERS + 1):
    num_items = random.randint(1, 5)
    for _ in range(num_items):
        product_id = random.randint(1, NUM_PRODUCTS)
        quantity = random.randint(1, 3)
        price = round(random.uniform(5.99, 999.99), 2)
        
        order_items.append({
            'order_item_id': item_id,
            'order_id': order_id,
            'product_id': product_id,
            'quantity': quantity,
            'price': price,
            'total': round(price * quantity, 2)
        })
        item_id += 1
    
    if order_id % 1000 == 0:
        print(f"   ✅ {order_id} order items processed...")

df_order_items = pd.DataFrame(order_items)
df_order_items.to_csv('data/order_items.csv', index=False)
print(f"✅ {len(order_items)} order items created!")

print("\n🎉 DATA GENERATION COMPLETE!")
print(f"📂 Files saved in 'data/' folder:")
print(f"   - customers.csv ({len(df_customers)} records)")
print(f"   - products.csv ({len(df_products)} records)")
print(f"   - orders.csv ({len(df_orders)} records)")
print(f"   - order_items.csv ({len(df_order_items)} records)")