import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="E-Commerce Analytics",
    page_icon="📊",
    layout="wide"
)

st.markdown("""

    <style>
        .reportview-container .main .block-container {
            padding-top: 2rem;
        }
        .css-1r6slb0 {
            background-color: #f8f9fa;
        }
        .stMetric {
            background-color: white;
            padding: 15px;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .css-1d391kg {
            padding: 1rem;
        }
    </style>

""", unsafe_allow_html=True)

st.title("📊 E-Commerce Analytics Dashboard")
st.markdown("---")

conn = sqlite3.connect('ecommerce.db')

# KPI Cards
col1, col2, col3, col4 = st.columns(4)

df_customers = pd.read_sql("SELECT COUNT(*) as total FROM customers", conn)
col1.metric("👥 Total Customers", df_customers['total'][0])

df_orders = pd.read_sql("SELECT COUNT(*) as total FROM orders", conn)
col2.metric("📦 Total Orders", df_orders['total'][0])

df_revenue = pd.read_sql("SELECT ROUND(SUM(total_amount), 2) as total FROM orders", conn)
col3.metric("💰 Total Revenue", f"₹{df_revenue['total'][0]:,.2f}")

df_avg = pd.read_sql("SELECT ROUND(AVG(total_amount), 2) as avg FROM orders", conn)
col4.metric("📊 Avg Order Value", f"₹{df_avg['avg'][0]:.2f}")

# Main Charts
col1, col2 = st.columns(2)

with col1:
    st.subheader("📈 Daily Revenue")
    df_daily = pd.read_sql("""
        SELECT DATE(order_date) as date, SUM(total_amount) as revenue
        FROM orders
        GROUP BY DATE(order_date)
        ORDER BY date DESC
        LIMIT 30
    """, conn)
    st.line_chart(df_daily.set_index('date'))

with col2:
    st.subheader("🏷️ Category-wise Sales")
    df_cat_sales = pd.read_sql("""
        SELECT p.category, ROUND(SUM(oi.total), 2) as revenue
        FROM order_items oi
        JOIN products p ON oi.product_id = p.product_id
        GROUP BY p.category
        ORDER BY revenue DESC
    """, conn)
    st.bar_chart(df_cat_sales.set_index('category'))

# Secondary Charts
col3, col4 = st.columns(2)

with col3:
    st.subheader("📅 Monthly Revenue Trend")
    df_monthly = pd.read_sql("""
        SELECT 
            strftime('%Y-%m', order_date) as month,
            ROUND(SUM(total_amount), 2) as revenue
        FROM orders
        GROUP BY strftime('%Y-%m', order_date)
        ORDER BY month
    """, conn)
    st.line_chart(df_monthly.set_index('month'))

with col4:
    st.subheader("📊 Order Status Distribution")
    df_status = pd.read_sql("""
        SELECT 
            status,
            COUNT(*) as count
        FROM orders
        GROUP BY status
    """, conn)
    st.bar_chart(df_status.set_index('status'))

st.markdown("---")

# ============= RFM Analysis (Customer Segmentation) =============
st.subheader("👤 RFM Analysis - Top Customers")
df_rfm = pd.read_sql("""
    WITH rfm_data AS (
        SELECT 
            c.customer_id,
            c.name,
            COUNT(o.order_id) as frequency,
            ROUND(SUM(o.total_amount), 2) as monetary,
            MAX(o.order_date) as last_order
        FROM customers c
        JOIN orders o ON c.customer_id = o.customer_id
        GROUP BY c.customer_id, c.name
    )
    SELECT 
        name as Customer,
        frequency as Orders,
        monetary as 'Total Spent (₹)',
        date(last_order) as 'Last Order'
    FROM rfm_data
    ORDER BY monetary DESC
    LIMIT 10
""", conn)
st.dataframe(df_rfm, use_container_width=True)

# ============= Category Performance =============
st.subheader("🏷️ Category-wise Performance")
df_category = pd.read_sql("""
    SELECT 
        p.category,
        COUNT(DISTINCT oi.order_id) as total_orders,
        SUM(oi.quantity) as units_sold,
        ROUND(AVG(oi.price), 2) as avg_price,
        ROUND(SUM(oi.total), 2) as revenue
    FROM order_items oi
    JOIN products p ON oi.product_id = p.product_id
    GROUP BY p.category
    ORDER BY revenue DESC
""", conn)
st.dataframe(df_category, use_container_width=True)

# ============= Download Button =============
st.subheader("📥 Export Data")
csv = df_category.to_csv(index=False)
st.download_button(
    label="📥 Download Category Data as CSV",
    data=csv,
    file_name="category_performance.csv",
    mime="text/csv"
)

# ============= Status Distribution =============
st.subheader("📊 Order Status Distribution")
df_status_detail = pd.read_sql("""
    SELECT 
        status,
        COUNT(*) as count,
        ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM orders), 2) as percentage
    FROM orders
    GROUP BY status
    ORDER BY count DESC
""", conn)
st.bar_chart(df_status_detail.set_index('status'))

conn.close()
