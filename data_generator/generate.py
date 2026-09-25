"""
Generate initial seed data into PostgreSQL.
Creates: customers, retailers, products, orders, order_items.
Run once to set up the source database.
"""

import random
from datetime import datetime, timedelta

import psycopg2
from faker import Faker

from config import PG_CONFIG, SEED_CONFIG, ZONES, CATEGORIES, STATUSES, TIERS, ORDER_STATUSES

fake = Faker()
random.seed(42)
Faker.seed(42)


def get_conn():
    return psycopg2.connect(**PG_CONFIG)


def create_tables(cur):
    cur.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            customer_id SERIAL PRIMARY KEY,
            name VARCHAR(200) NOT NULL,
            phone VARCHAR(20) NOT NULL,
            email VARCHAR(200) NOT NULL,
            tier VARCHAR(20) NOT NULL DEFAULT 'bronze',
            created_at TIMESTAMP NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMP NOT NULL DEFAULT NOW()
        );

        CREATE TABLE IF NOT EXISTS retailers (
            retailer_id SERIAL PRIMARY KEY,
            name VARCHAR(200) NOT NULL,
            zone VARCHAR(100) NOT NULL,
            category VARCHAR(50) NOT NULL,
            status VARCHAR(20) NOT NULL DEFAULT 'active',
            onboarded_at TIMESTAMP NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMP NOT NULL DEFAULT NOW()
        );

        CREATE TABLE IF NOT EXISTS products (
            product_id SERIAL PRIMARY KEY,
            name VARCHAR(200) NOT NULL,
            category VARCHAR(50) NOT NULL,
            price NUMERIC(10, 2) NOT NULL,
            created_at TIMESTAMP NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMP NOT NULL DEFAULT NOW()
        );

        CREATE TABLE IF NOT EXISTS orders (
            order_id SERIAL PRIMARY KEY,
            customer_id INT NOT NULL REFERENCES customers(customer_id),
            retailer_id INT NOT NULL REFERENCES retailers(retailer_id),
            zone VARCHAR(100) NOT NULL,
            status VARCHAR(20) NOT NULL DEFAULT 'pending',
            total_amount NUMERIC(12, 2) NOT NULL DEFAULT 0,
            created_at TIMESTAMP NOT NULL,
            updated_at TIMESTAMP NOT NULL
        );

        CREATE TABLE IF NOT EXISTS order_items (
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
    product_names = set()
    while len(product_names) < n:
        product_names.add(fake.catch_phrase())

    for name in product_names:
        cur.execute(
            """INSERT INTO products (name, category, price, created_at, updated_at)
               VALUES (%s, %s, %s, %s, %s)""",
            (
                name,
                random.choice(CATEGORIES),
                round(random.uniform(1.50, 500.00), 2),
                fake.date_time_between(start_date="-1y", end_date="-1M"),
                datetime.utcnow(),
            ),
        )


def seed_orders(cur, num_orders, num_customers, num_retailers, num_products, max_items, date_range_days):
    print(f"Seeding {num_orders} orders with up to {max_items} items each...")
    base_date = datetime.utcnow() - timedelta(days=date_range_days)

    for _ in range(num_orders):
        customer_id = random.randint(1, num_customers)
        retailer_id = random.randint(1, num_retailers)
        zone = random.choice(ZONES)
        status = random.choices(ORDER_STATUSES, weights=[5, 15, 70, 10])[0]
        order_date = base_date + timedelta(
            days=random.randint(0, date_range_days),
            hours=random.randint(6, 22),
            minutes=random.randint(0, 59),
        )

        cur.execute(
            """INSERT INTO orders (customer_id, retailer_id, zone, status, total_amount, created_at, updated_at)
               VALUES (%s, %s, %s, %s, 0, %s, %s) RETURNING order_id""",
            (customer_id, retailer_id, zone, status, order_date, order_date),
        )
        order_id = cur.fetchone()[0]

        # Generate line items
        num_items = random.randint(1, max_items)
        order_total = 0

        for _ in range(num_items):
            product_id = random.randint(1, num_products)
            quantity = random.randint(1, 4)
            unit_price = round(random.uniform(2.00, 250.00), 2)
            line_total = round(quantity * unit_price, 2)
            order_total += line_total

            cur.execute(
                """INSERT INTO order_items (order_id, product_id, product_name, quantity, unit_price, created_at)
                   VALUES (%s, %s, %s, %s, %s, %s)""",
                (
                    order_id,
                    product_id,
                    fake.catch_phrase(),
                    quantity,
                    unit_price,
                    order_date,
                ),
            )

        # Update order total
        cur.execute(
            "UPDATE orders SET total_amount = %s WHERE order_id = %s",
            (round(order_total, 2), order_id),
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
