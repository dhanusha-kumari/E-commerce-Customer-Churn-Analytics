import sqlite3
import random
import pandas as pd
from datetime import datetime, timedelta
import os

DB_PATH = "ecommerce.db"

def init_db(db_path=DB_PATH, force=False):
    """
    Initializes the SQLite database with 'customers' and 'orders' tables,
    populating them with realistic synthetic dataset if empty or force=True.
    """
    if os.path.exists(db_path) and not force:
        print(f"Database {db_path} already exists.")
        return

    print(f"Initializing database at {db_path}...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Drop existing tables if re-initializing
    cursor.execute("DROP TABLE IF EXISTS orders")
    cursor.execute("DROP TABLE IF EXISTS customers")

    # Create relational tables
    cursor.execute("""
    CREATE TABLE customers (
        customer_id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        email TEXT NOT NULL,
        category TEXT NOT NULL,
        join_date DATE NOT NULL,
        country TEXT NOT NULL
    )
    """)

    cursor.execute("""
    CREATE TABLE orders (
        order_id TEXT PRIMARY KEY,
        customer_id TEXT NOT NULL,
        order_date DATE NOT NULL,
        amount REAL NOT NULL,
        item_count INTEGER NOT NULL,
        category TEXT NOT NULL,
        status TEXT NOT NULL,
        FOREIGN KEY (customer_id) REFERENCES customers (customer_id)
    )
    """)

    # Seed data generator settings
    random.seed(42)
    categories = ["Electronics", "Fashion & Apparel", "Home & Kitchen", "Beauty & Personal Care", "Sports & Outdoors"]
    countries = ["United States", "United Kingdom", "Canada", "Germany", "Australia", "India", "France"]
    first_names = ["Emma", "Liam", "Olivia", "Noah", "Ava", "Ethan", "Sophia", "Mason", "Isabella", "William",
                   "Mia", "James", "Charlotte", "Benjamin", "Amelia", "Lucas", "Harper", "Alexander", "Evelyn", "Daniel",
                   "Priya", "Rahul", "Ananya", "Vikram", "Sneha", "Arjun", "Kavya", "Rohan", "Pooja", "Siddharth"]
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez",
                  "Sharma", "Verma", "Patel", "Reddy", "Nair", "Kumar", "Singh", "Rao", "Gupta", "Deshmukh"]

    num_customers = 350
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2026, 7, 20)
    total_days = (end_date - start_date).days

    customers_data = []
    orders_data = []

    for i in range(1, num_customers + 1):
        cust_id = f"CUST_{i:04d}"
        fname = random.choice(first_names)
        lname = random.choice(last_names)
        name = f"{fname} {lname}"
        email = f"{fname.lower()}.{lname.lower()}{i}@example.com"
        pref_category = random.choice(categories)
        country = random.choice(countries)
        
        # Join date randomly in past 2.5 years
        join_days_offset = random.randint(0, int(total_days * 0.8))
        cust_join_date = start_date + timedelta(days=join_days_offset)
        join_date_str = cust_join_date.strftime("%Y-%m-%d")

        customers_data.append((cust_id, name, email, pref_category, join_date_str, country))

        # Assign customer churn behavior profile:
        # 0: Active High Value, 1: Regular Active, 2: At-Risk Inactive, 3: Churned / Lapsed
        behavior_type = random.choices([0, 1, 2, 3], weights=[0.25, 0.40, 0.20, 0.15])[0]

        if behavior_type == 0: # Active High Value
            num_orders = random.randint(8, 25)
            last_activity_cutoff = end_date - timedelta(days=random.randint(2, 35))
        elif behavior_type == 1: # Regular Active
            num_orders = random.randint(3, 10)
            last_activity_cutoff = end_date - timedelta(days=random.randint(5, 60))
        elif behavior_type == 2: # At-Risk Inactive
            num_orders = random.randint(2, 6)
            last_activity_cutoff = end_date - timedelta(days=random.randint(65, 150))
        else: # Churned / Lapsed
            num_orders = random.randint(1, 4)
            last_activity_cutoff = end_date - timedelta(days=random.randint(155, 450))

        # Ensure last activity is after join date
        if last_activity_cutoff < cust_join_date:
            last_activity_cutoff = cust_join_date + timedelta(days=10)

        # Generate orders spread between join date and last activity
        span_days = max(1, (last_activity_cutoff - cust_join_date).days)

        for o_idx in range(1, num_orders + 1):
            order_id = f"ORD_{i:04d}_{o_idx:02d}"
            order_days_offset = random.randint(0, span_days)
            order_dt = cust_join_date + timedelta(days=order_days_offset)
            order_date_str = order_dt.strftime("%Y-%m-%d")

            # Pricing based on category
            order_cat = pref_category if random.random() < 0.7 else random.choice(categories)
            if order_cat == "Electronics":
                amount = round(random.uniform(80.0, 1200.0), 2)
            elif order_cat == "Fashion & Apparel":
                amount = round(random.uniform(25.0, 300.0), 2)
            elif order_cat == "Home & Kitchen":
                amount = round(random.uniform(40.0, 600.0), 2)
            elif order_cat == "Beauty & Personal Care":
                amount = round(random.uniform(15.0, 180.0), 2)
            else:
                amount = round(random.uniform(30.0, 450.0), 2)

            item_count = random.randint(1, 6)
            status = random.choices(["Completed", "Returned", "Cancelled"], weights=[0.88, 0.08, 0.04])[0]

            orders_data.append((order_id, cust_id, order_date_str, amount, item_count, order_cat, status))

    cursor.executemany("INSERT INTO customers VALUES (?, ?, ?, ?, ?, ?)", customers_data)
    cursor.executemany("INSERT INTO orders VALUES (?, ?, ?, ?, ?, ?, ?)", orders_data)

    conn.commit()
    conn.close()
    print(f"Database successfully populated with {len(customers_data)} customers and {len(orders_data)} orders.")


def get_customer_summary_sql(db_path=DB_PATH):
    """
    Executes a custom SQL query with JOIN and GROUP BY to compute aggregated customer purchase metrics.
    """
    conn = sqlite3.connect(db_path)
    query = """
    SELECT 
        c.customer_id,
        c.name,
        c.email,
        c.category AS preferred_category,
        c.country,
        c.join_date,
        COUNT(CASE WHEN o.status = 'Completed' THEN o.order_id END) AS total_orders,
        COALESCE(SUM(CASE WHEN o.status = 'Completed' THEN o.amount ELSE 0 END), 0.0) AS total_spent,
        COALESCE(AVG(CASE WHEN o.status = 'Completed' THEN o.amount END), 0.0) AS avg_order_value,
        MAX(CASE WHEN o.status = 'Completed' THEN o.order_date END) AS last_order_date,
        MIN(CASE WHEN o.status = 'Completed' THEN o.order_date END) AS first_order_date,
        COUNT(CASE WHEN o.status = 'Returned' THEN o.order_id END) AS returned_orders
    FROM customers c
    LEFT JOIN orders o ON c.customer_id = o.customer_id
    GROUP BY c.customer_id, c.name, c.email, c.category, c.country, c.join_date
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df


def get_monthly_sales_sql(db_path=DB_PATH):
    """
    SQL query to get monthly revenue, completed order count, and distinct active customers.
    """
    conn = sqlite3.connect(db_path)
    query = """
    SELECT 
        strftime('%Y-%m', order_date) AS year_month,
        SUM(amount) AS monthly_revenue,
        COUNT(order_id) AS total_orders,
        COUNT(DISTINCT customer_id) AS active_customers,
        AVG(amount) AS avg_order_amount
    FROM orders
    WHERE status = 'Completed'
    GROUP BY year_month
    ORDER BY year_month ASC
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df


def get_raw_orders_sql(db_path=DB_PATH):
    """
    Fetch raw order records joined with customer data for analysis & filtering.
    """
    conn = sqlite3.connect(db_path)
    query = """
    SELECT 
        o.order_id,
        o.customer_id,
        c.name AS customer_name,
        c.category AS customer_category,
        c.country,
        o.order_date,
        o.amount,
        o.item_count,
        o.category AS product_category,
        o.status
    FROM orders o
    JOIN customers c ON o.customer_id = c.customer_id
    ORDER BY o.order_date DESC
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

if __name__ == "__main__":
    init_db(force=True)
    df_summary = get_customer_summary_sql()
    print("\nSample Customer Summary SQL Query Output:")
    print(df_summary.head())
