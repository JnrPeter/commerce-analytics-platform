"""
Simulate real-world data mutations for SCD tracking.
Run this multiple times to build up change history:
  - Retailers change zones, get suspended/reactivated, rebrand
  - Customers upgrade tiers, update emails
  - New orders arrive (with full financial and delivery fields)
Each run represents a "day" of operational changes.
"""

import random
from datetime import datetime, timedelta

import psycopg2
from faker import Faker

from config import (
    PG_CONFIG, MUTATE_CONFIG, ZONES, STATUSES, TIERS,
    ORDER_STATUSES, PAYMENT_METHODS, ORDER_CHANNELS,
)

fake = Faker()


def get_conn():
    return psycopg2.connect(**PG_CONFIG)


def add_new_orders(cur, n):
    """Generate new orders to simulate ongoing business."""
    print(f"Adding {n} new orders...")

    cur.execute("SELECT count(*) FROM customers")
    num_customers = cur.fetchone()[0]
    cur.execute("SELECT count(*) FROM retailers")
    num_retailers = cur.fetchone()[0]
    cur.execute("SELECT count(*) FROM products")
    num_products = cur.fetchone()[0]

    now = datetime.utcnow()

    for _ in range(n):
        customer_id = random.randint(1, num_customers)
        retailer_id = random.randint(1, num_retailers)
        zone = random.choice(ZONES)
        status = random.choices(ORDER_STATUSES, weights=[5, 15, 70, 10])[0]
        payment_method = random.choices(PAYMENT_METHODS, weights=[60, 30, 10])[0]
        order_channel = random.choices(ORDER_CHANNELS, weights=[65, 30, 5])[0]
        order_date = now - timedelta(hours=random.randint(0, 23), minutes=random.randint(0, 59))

        # Generate items and subtotal
        num_items = random.randint(1, 5)
        items = []
        subtotal = 0

        for _ in range(num_items):
            product_id = random.randint(1, num_products)
            quantity = random.randint(1, 4)
            unit_price = round(random.uniform(2.00, 250.00), 2)
            subtotal += quantity * unit_price
            items.append((product_id, fake.catch_phrase(), quantity, unit_price))

        subtotal = round(subtotal, 2)

        # Financial fields
        has_discount = random.random() < 0.25
        discount_amount = round(subtotal * random.uniform(0.05, 0.20), 2) if has_discount else 0
        delivery_fee = round(random.uniform(3.00, 15.00), 2)
        total_amount = round(subtotal - discount_amount + delivery_fee, 2)

        # Delivery performance
        estimated_delivery_minutes = random.choice([30, 45, 60, 90])

        if status == 'delivered':
            variance = random.gauss(0, 15)
            actual_delivery_minutes = max(10, int(estimated_delivery_minutes + variance))
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

        for product_id, product_name, quantity, unit_price in items:
            cur.execute(
                """INSERT INTO order_items (order_id, product_id, product_name, quantity, unit_price, created_at)
                   VALUES (%s, %s, %s, %s, %s, %s)""",
                (order_id, product_id, product_name, quantity, unit_price, order_date),
            )


def change_retailer_zones(cur, n):
    """Simulate retailers moving zones (triggers SCD2)."""
    print(f"Changing {n} retailer zones...")
    cur.execute("SELECT retailer_id, zone FROM retailers WHERE status = 'active' ORDER BY RANDOM() LIMIT %s", (n,))
    rows = cur.fetchall()

    for retailer_id, current_zone in rows:
        new_zone = random.choice([z for z in ZONES if z != current_zone])
        cur.execute(
            "UPDATE retailers SET zone = %s, updated_at = NOW() WHERE retailer_id = %s",
            (new_zone, retailer_id),
        )
        print(f"  Retailer {retailer_id}: {current_zone} -> {new_zone}")


def change_retailer_statuses(cur, n):
    """Simulate retailers getting suspended or reactivated (triggers SCD2)."""
    print(f"Changing {n} retailer statuses...")
    cur.execute("SELECT retailer_id, status FROM retailers ORDER BY RANDOM() LIMIT %s", (n,))
    rows = cur.fetchall()

    for retailer_id, current_status in rows:
        new_status = random.choice([s for s in STATUSES if s != current_status])
        cur.execute(
            "UPDATE retailers SET status = %s, updated_at = NOW() WHERE retailer_id = %s",
            (new_status, retailer_id),
        )
        print(f"  Retailer {retailer_id}: {current_status} -> {new_status}")


def upgrade_customer_tiers(cur, n):
    """Simulate customer tier upgrades (triggers SCD1 overwrite)."""
    print(f"Upgrading {n} customer tiers...")
    cur.execute(
        "SELECT customer_id, tier FROM customers WHERE tier != 'platinum' ORDER BY RANDOM() LIMIT %s", (n,)
    )
    rows = cur.fetchall()

    tier_order = TIERS
    for customer_id, current_tier in rows:
        idx = tier_order.index(current_tier)
        if idx < len(tier_order) - 1:
            new_tier = tier_order[idx + 1]
            cur.execute(
                "UPDATE customers SET tier = %s, updated_at = NOW() WHERE customer_id = %s",
                (new_tier, customer_id),
            )
            print(f"  Customer {customer_id}: {current_tier} -> {new_tier}")


def update_customer_emails(cur, n):
    """Simulate customers updating their email (triggers SCD1 overwrite)."""
    print(f"Updating {n} customer emails...")
    cur.execute("SELECT customer_id FROM customers ORDER BY RANDOM() LIMIT %s", (n,))
    rows = cur.fetchall()

    for (customer_id,) in rows:
        cur.execute(
            "UPDATE customers SET email = %s, updated_at = NOW() WHERE customer_id = %s",
            (fake.email(), customer_id),
        )


def change_product_prices(cur, n):
    """Simulate product price adjustments (triggers SCD2 on dim_products)."""
    print(f"Changing {n} product prices...")
    cur.execute("SELECT product_id, price FROM products ORDER BY RANDOM() LIMIT %s", (n,))
    rows = cur.fetchall()

    for product_id, current_price in rows:
        # Adjust price by -15% to +15%, minimum 1.50
        change_pct = random.uniform(-0.15, 0.15)
        new_price = max(1.50, round(float(current_price) * (1 + change_pct), 2))
        cur.execute(
            "UPDATE products SET price = %s, updated_at = NOW() WHERE product_id = %s",
            (new_price, product_id),
        )
        direction = "up" if new_price > float(current_price) else "down"
        print(f"  Product {product_id}: {current_price} -> {new_price} ({direction})")


def main():
    conn = get_conn()
    cur = conn.cursor()

    add_new_orders(cur, MUTATE_CONFIG["new_orders"])
    change_retailer_zones(cur, MUTATE_CONFIG["retailer_zone_changes"])
    change_retailer_statuses(cur, MUTATE_CONFIG["retailer_status_changes"])
    upgrade_customer_tiers(cur, MUTATE_CONFIG["customer_tier_upgrades"])
    update_customer_emails(cur, MUTATE_CONFIG["customer_email_updates"])
    change_product_prices(cur, MUTATE_CONFIG["product_price_changes"])

    conn.commit()
    cur.close()
    conn.close()
    print("Mutation complete.")


if __name__ == "__main__":
    main()
