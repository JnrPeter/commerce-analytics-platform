import os
from dotenv import load_dotenv

load_dotenv()

# PostgreSQL connection
PG_CONFIG = {
    "host": os.getenv("PG_HOST", "localhost"),
    "port": int(os.getenv("PG_PORT", 5433)),
    "database": os.getenv("PG_DATABASE", "commerce"),
    "user": os.getenv("PG_USER", "commerce_user"),
    "password": os.getenv("PG_PASSWORD", "commerce_pass"),
}

# Volume knobs
SEED_CONFIG = {
    "num_customers": 4000,
    "num_retailers": 1000,
    "num_products": 1000,
    "num_orders": 20000,
    "max_items_per_order": 5,
    "date_range_days": 365,
}

# Mutation knobs
MUTATE_CONFIG = {
    "new_orders": 500,
    "retailer_zone_changes": 8,
    "retailer_status_changes": 5,
    "customer_tier_upgrades": 25,
    "customer_email_updates": 15,
}

# Zones
ZONES = [
    "Downtown", "Westside", "Eastgate", "Northridge", "Southbank",
    "Riverside", "Hilltop", "Lakewood", "Midtown", "Old Quarter",
    "Harbor District", "Greenfield", "Sunset Park", "Brookdale", "Crescent Bay",
]

# Retailer categories
CATEGORIES = [
    "Restaurant", "Grocery", "Pharmacy", "Electronics",
    "Fashion", "Beauty", "Home & Garden", "Sports",
]

# Retailer statuses
STATUSES = ["active", "suspended", "churned", "onboarding"]

# Customer tiers
TIERS = ["bronze", "silver", "gold", "platinum"]

# Order statuses
ORDER_STATUSES = ["pending", "confirmed", "delivered", "cancelled"]

# Payment methods
PAYMENT_METHODS = ["mobile_money", "card", "cash_on_delivery"]

# Order channels
ORDER_CHANNELS = ["mobile_app", "web", "ussd"]
