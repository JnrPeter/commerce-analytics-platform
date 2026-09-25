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

# Volume knobs — adjust these to control data size
SEED_CONFIG = {
    "num_customers": 500,
    "num_retailers": 50,
    "num_products": 200,
    "num_orders": 5000,
    "max_items_per_order": 5,
    "date_range_days": 365,  # orders spread across this many days
}

# Mutation knobs — controls how much changes per mutation run
MUTATE_CONFIG = {
    "new_orders": 200,
    "retailer_zone_changes": 3,
    "retailer_status_changes": 2,
    "customer_tier_upgrades": 10,
    "customer_email_updates": 5,
}

# Zones for retailer assignment
ZONES = [
    "Accra Central", "East Legon", "Madina", "Tema", "Kasoa",
    "Achimota", "Dansoman", "Spintex", "Airport City", "Osu",
    "Labone", "Cantonments", "Adenta", "Teshie", "Labadi",
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
