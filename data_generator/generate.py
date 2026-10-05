"""
Generate initial seed data into PostgreSQL.
Creates: customers, retailers, products, orders, order_items.
Run once to set up the source database.
"""

import random
from datetime import datetime, timedelta

import psycopg2
from faker import Faker

from config import (
    PG_CONFIG, SEED_CONFIG, ZONES, CATEGORIES, STATUSES,
    TIERS, ORDER_STATUSES, PAYMENT_METHODS, ORDER_CHANNELS,
    PRODUCT_NAMES,
)

fake = Faker()
random.seed(42)
Faker.seed(42)


def get_conn():
    return psycopg2.connect(**PG_CONFIG)


def create_tables(cur):
    cur.execute("""
        DROP TABLE IF EXISTS order_items CASCADE;
        DROP TABLE IF EXISTS orders CASCADE;
        DROP TABLE IF EXISTS products CASCADE;
        DROP TABLE IF EXISTS retailers CASCADE;
        DROP TABLE IF EXISTS customers CASCADE;

        CREATE TABLE customers (
            customer_id SERIAL PRIMARY KEY,
            name VARCHAR(200) NOT NULL,
            phone VARCHAR(20) NOT NULL,
            email VARCHAR(200) NOT NULL,
            tier VARCHAR(20) NOT NULL DEFAULT 'bronze',
            created_at TIMESTAMP NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMP NOT NULL DEFAULT NOW()
        );

        CREATE TABLE retailers (
            retailer_id SERIAL PRIMARY KEY,
            name VARCHAR(200) NOT NULL,
            zone VARCHAR(100) NOT NULL,
            category VARCHAR(50) NOT NULL,
            status VARCHAR(20) NOT NULL DEFAULT 'active',
            onboarded_at TIMESTAMP NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMP NOT NULL DEFAULT NOW()
        );

        CREATE TABLE products (
            product_id SERIAL PRIMARY KEY,
            name VARCHAR(200) NOT NULL,
            category VARCHAR(50) NOT NULL,
            price NUMERIC(10, 2) NOT NULL,
            created_at TIMESTAMP NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMP NOT NULL DEFAULT NOW()
        );

        CREATE TABLE orders (
            order_id SERIAL PRIMARY KEY,
            customer_id INT NOT NULL REFERENCES customers(customer_id),
            retailer_id INT NOT NULL REFERENCES retailers(retailer_id),
            zone VARCHAR(100) NOT NULL,
            status VARCHAR(20) NOT NULL DEFAULT 'pending',
            payment_method VARCHAR(30) NOT NULL DEFAULT 'mobile_money',
            order_channel VARCHAR(20) NOT NULL DEFAULT 'mobile_app',
            subtotal NUMERIC(12, 2) NOT NULL DEFAULT 0,
            discount_amount NUMERIC(10, 2) NOT NULL DEFAULT 0,
            delivery_fee NUMERIC(10, 2) NOT NULL DEFAULT 0,
            total_amount NUMERIC(12, 2) NOT NULL DEFAULT 0,
            estimated_delivery_minutes INT,
            actual_delivery_minutes INT,
            rating SMALLINT,
            created_at TIMESTAMP NOT NULL,
            updated_at TIMESTAMP NOT NULL
        );

        CREATE TABLE order_items (
            item_id SERIAL PRIMARY KEY,
            order_id INT NOT NULL REFERENCES orders(order_id),
            product_id INT NOT NULL REFERENCES products(product_id),
            product_name VARCHAR(200) NOT NULL,
            quantity INT NOT NULL DEFAULT 1,
            unit_price NUMERIC(10, 2) NOT NULL,
            created_at TIMESTAMP NOT NULL
        );
    """)


def seed_customers(cur, n):
    print(f"Seeding {n} customers...")
    for _ in range(n):
        cur.execute(
            """INSERT INTO customers (name, phone, email, tier, created_at, updated_at)
               VALUES (%s, %s, %s, %s, %s, %s)""",
            (
                fake.name(),
                fake.phone_number()[:20],
                fake.email(),
                random.choice(TIERS),
                fake.date_time_between(start_date="-2y", end_date="-6M"),
                datetime.utcnow(),
            ),
        )


def seed_retailers(cur, n):
    print(f"Seeding {n} retailers...")
    for _ in range(n):
        cat = random.choice(CATEGORIES)
        cur.execute(
            """INSERT INTO retailers (name, zone, category, status, onboarded_at, updated_at)
               VALUES (%s, %s, %s, %s, %s, %s)""",
            (
                f"{fake.company()} {cat}",
                random.choice(ZONES),
                cat,
                random.choices(STATUSES, weights=[80, 5, 5, 10])[0],
                fake.date_time_between(start_date="-2y", end_date="-3M"),
                datetime.utcnow(),
            ),
        )


def seed_products(cur, n):
    print(f"Seeding {n} products...")

    # Price ranges per category (min, max)
    price_ranges = {
        "Restaurant": (5.00, 80.00),
        "Grocery": (1.50, 60.00),
        "Pharmacy": (2.00, 120.00),
        "Electronics": (5.00, 500.00),
        "Fashion": (10.00, 300.00),
        "Beauty": (3.00, 150.00),
        "Home & Garden": (5.00, 250.00),
        "Sports": (5.00, 200.00),
    }

    # Build a pool of (name, category) pairs from PRODUCT_NAMES
    product_pool = []
    for category, names in PRODUCT_NAMES.items():
        for name in names:
            product_pool.append((name, category))

    # If we need more than the pool, add numbered variants
    while len(product_pool) < n:
        cat = random.choice(CATEGORIES)
        base_name = random.choice(PRODUCT_NAMES[cat])
        variant = f"{base_name} (v{random.randint(2, 9)})"
        product_pool.append((variant, cat))

    random.shuffle(product_pool)
    selected = product_pool[:n]

    for name, category in selected:
        min_price, max_price = price_ranges[category]
        cur.execute(
            """INSERT INTO products (name, category, price, created_at, updated_at)
               VALUES (%s, %s, %s, %s, %s)""",
            (
                name,
                category,
                round(random.uniform(min_price, max_price), 2),
                fake.date_time_between(start_date="-1y", end_date="-1M"),
                datetime.utcnow(),
            ),
        )


def seed_orders(cur, num_orders, num_customers, num_retailers, num_products, max_items, date_range_days):
    print(f"Seeding {num_orders} orders with up to {max_items} items each...")
    base_date = datetime.utcnow() - timedelta(days=date_range_days)

    # Pre-load product names and prices for realistic order items
    cur.execute("SELECT product_id, name, price FROM products")
    product_lookup = {row[0]: (row[1], float(row[2])) for row in cur.fetchall()}

    for i in range(num_orders):
        if (i + 1) % 5000 == 0:
            print(f"  ...{i + 1}/{num_orders} orders")

        customer_id = random.randint(1, num_customers)
        retailer_id = random.randint(1, num_retailers)
        zone = random.choice(ZONES)
        status = random.choices(ORDER_STATUSES, weights=[5, 15, 70, 10])[0]
        payment_method = random.choices(PAYMENT_METHODS, weights=[60, 30, 10])[0]
        order_channel = random.choices(ORDER_CHANNELS, weights=[65, 30, 5])[0]

        order_date = base_date + timedelta(
            days=random.randint(0, date_range_days),
            hours=random.randint(6, 22),
            minutes=random.randint(0, 59),
        )

        # Generate line items using actual product names and prices
        num_items = random.randint(1, max_items)
        items = []
        subtotal = 0

        for _ in range(num_items):
            product_id = random.randint(1, num_products)
            product_name, base_price = product_lookup.get(product_id, ("Unknown Product", 10.00))
            quantity = random.randint(1, 4)
            # Small price variance (+/- 10%) to simulate different sizes/options
            unit_price = round(base_price * random.uniform(0.90, 1.10), 2)
            line_total = round(quantity * unit_price, 2)
            subtotal += line_total
            items.append((product_id, product_name, quantity, unit_price))

        subtotal = round(subtotal, 2)

        # Financial fields
        has_discount = random.random() < 0.25  # 25% of orders get a discount
        discount_amount = round(subtotal * random.uniform(0.05, 0.20), 2) if has_discount else 0
        delivery_fee = round(random.uniform(3.00, 15.00), 2)
        total_amount = round(subtotal - discount_amount + delivery_fee, 2)

        # Delivery performance
        estimated_delivery_minutes = random.choice([30, 45, 60, 90])

        if status == 'delivered':
            # Actual delivery: usually close to estimate, sometimes late
            variance = random.gauss(0, 15)
            actual_delivery_minutes = max(10, int(estimated_delivery_minutes + variance))
            # Rating: correlated with delivery performance
            delay = actual_delivery_minutes - estimated_delivery_minutes
            if delay <= 0:
                rating = random.choices([4, 5], weights=[30, 70])[0]
            elif delay <= 15:
                rating = random.choices([3, 4, 5], weights=[20, 50, 30])[0]
            elif delay <= 30:
                rating = random.choices([2, 3, 4], weights=[30, 50, 20])[0]
            else:
                rating = random.choices([1, 2, 3], weights=[40, 40, 20])[0]
        elif status == 'cancelled':
            actual_delivery_minutes = None
            rating = None
        else:
            # pending or confirmed: not yet delivered
            actual_delivery_minutes = None
            rating = None

        cur.execute(
            """INSERT INTO orders (
                customer_id, retailer_id, zone, status,
                payment_method, order_channel,
                subtotal, discount_amount, delivery_fee, total_amount,
                estimated_delivery_minutes, actual_delivery_minutes, rating,
                created_at, updated_at
            ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING order_id""",
            (
                customer_id, retailer_id, zone, status,
                payment_method, order_channel,
                subtotal, discount_amount, delivery_fee, total_amount,
                estimated_delivery_minutes, actual_delivery_minutes, rating,
                order_date, order_date,
            ),
        )
        order_id = cur.fetchone()[0]

        # Insert line items
        for product_id, product_name, quantity, unit_price in items:
            cur.execute(
                """INSERT INTO order_items (order_id, product_id, product_name, quantity, unit_price, created_at)
                   VALUES (%s, %s, %s, %s, %s, %s)""",
                (order_id, product_id, product_name, quantity, unit_price, order_date),
            )


def main():
    conn = get_conn()
    cur = conn.cursor()

    print("Creating tables...")
    create_tables(cur)
    conn.commit()

    seed_customers(cur, SEED_CONFIG["num_customers"])
    seed_retailers(cur, SEED_CONFIG["num_retailers"])
    seed_products(cur, SEED_CONFIG["num_products"])
    seed_orders(
        cur,
        SEED_CONFIG["num_orders"],
        SEED_CONFIG["num_customers"],
        SEED_CONFIG["num_retailers"],
        SEED_CONFIG["num_products"],
        SEED_CONFIG["max_items_per_order"],
        SEED_CONFIG["date_range_days"],
    )

    conn.commit()
    cur.close()
    conn.close()
    print("Seed complete.")


if __name__ == "__main__":
    main()
