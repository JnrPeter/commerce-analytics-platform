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
    "product_price_changes": 15,
}

# Zones
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

# Payment methods
PAYMENT_METHODS = ["mobile_money", "card", "cash_on_delivery"]

# Order channels
ORDER_CHANNELS = ["mobile_app", "web", "ussd"]

# Product names by category (realistic e-commerce items)
PRODUCT_NAMES = {
    "Restaurant": [
        "Jollof Rice Plate", "Grilled Chicken Combo", "Fried Rice Box", "Banku & Tilapia",
        "Waakye Special", "Fufu & Light Soup", "Kelewele & Chicken", "Red Red & Plantain",
        "Club Sandwich", "Beef Burger", "Chicken Wrap", "Pepperoni Pizza",
        "Margherita Pizza", "Caesar Salad", "Fish & Chips", "Spaghetti Bolognese",
        "Chicken Fried Rice", "Shawarma Wrap", "Meat Pie", "Spring Rolls (6pc)",
        "Chicken Wings (8pc)", "BBQ Ribs Plate", "Veggie Stir Fry", "Pad Thai Noodles",
        "Butter Chicken Rice", "Lamb Kebab Plate", "Tilapia & Chips", "Goat Pepper Soup",
        "Yam & Palava Sauce", "Omo Tuo & Groundnut Soup",
    ],
    "Grocery": [
        "Basmati Rice 5kg", "Cooking Oil 3L", "Tomato Paste 400g", "Whole Wheat Bread",
        "Fresh Milk 1L", "Eggs (Crate of 30)", "Sugar 2kg", "Salt 1kg",
        "Canned Tuna 150g", "Instant Noodles (Pack of 10)", "Bottled Water 1.5L (6pk)",
        "Orange Juice 1L", "Frozen Chicken 1kg", "Spaghetti 500g", "Cornflakes 500g",
        "Peanut Butter 500g", "Milo 400g", "Nescafe 200g", "Tea Bags (Box of 50)",
        "Sardines 125g", "Baked Beans 400g", "Mayonnaise 500ml", "Ketchup 500ml",
        "Butter 250g", "Cheese Slices (Pack of 10)", "Yoghurt 500ml", "Apple (1kg)",
        "Banana Bunch", "Onions 2kg", "Garlic 500g",
    ],
    "Pharmacy": [
        "Paracetamol 500mg (20 tabs)", "Vitamin C 1000mg (30 tabs)", "Ibuprofen 400mg (10 tabs)",
        "Cough Syrup 100ml", "Multivitamin Complex (60 caps)", "Antacid Tablets (20 tabs)",
        "Bandage Roll 5cm", "Hand Sanitizer 500ml", "Face Masks (Box of 50)",
        "Digital Thermometer", "Blood Pressure Monitor", "First Aid Kit",
        "Eye Drops 10ml", "Allergy Relief (30 tabs)", "Zinc Supplements (30 tabs)",
        "Omega-3 Fish Oil (60 caps)", "Calcium + Vitamin D (30 tabs)", "Iron Supplements (30 tabs)",
        "Antiseptic Cream 50g", "Plasters (Box of 100)", "Cotton Wool 100g",
        "Insect Repellent Spray", "Sunscreen SPF50 100ml", "Lip Balm SPF30",
        "Baby Diapers (Pack of 24)", "Baby Wipes (Pack of 80)", "Pregnancy Test Kit",
        "Oral Rehydration Salts (10 sachets)", "Nasal Spray 20ml", "Throat Lozenges (24pc)",
    ],
    "Electronics": [
        "USB-C Charging Cable 1m", "Wireless Earbuds", "Phone Case (Universal)",
        "Screen Protector", "Power Bank 10000mAh", "Bluetooth Speaker",
        "Laptop Sleeve 15 inch", "Mouse Pad", "Wireless Mouse", "USB Flash Drive 32GB",
        "HDMI Cable 2m", "Webcam 1080p", "LED Desk Lamp", "Surge Protector 4-Outlet",
        "Keyboard (Wireless)", "Earphone Splitter", "Car Phone Mount",
        "Portable SSD 500GB", "Micro SD Card 64GB", "USB Hub 4-Port",
        "Smart Plug WiFi", "Ring Light 10 inch", "Laptop Stand (Adjustable)",
        "Cable Organizer Kit", "Noise Cancelling Headphones", "Action Camera",
        "Portable Monitor 15 inch", "Smart Watch Band", "Phone Tripod", "VR Headset",
    ],
    "Fashion": [
        "Cotton T-Shirt (Unisex)", "Slim Fit Jeans", "Polo Shirt", "Casual Sneakers",
        "Leather Belt", "Sunglasses (UV400)", "Baseball Cap", "Wrist Watch (Analog)",
        "Canvas Backpack", "Tote Bag", "Ankara Print Dress", "Kente Scarf",
        "Denim Jacket", "Chino Pants", "Hoodie (Pullover)", "Running Shoes",
        "Flip Flops", "Dress Shirt (Slim Fit)", "Maxi Skirt", "Swimwear Set",
        "Beanie Hat", "Silk Tie", "Cufflinks Set", "Leather Wallet",
        "Crossbody Bag", "Rain Jacket", "Jogger Pants", "Formal Shoes (Oxford)",
        "Sports Shorts", "Compression Socks (3-Pack)",
    ],
    "Beauty": [
        "Shea Butter Moisturizer 200ml", "Coconut Oil Hair Serum 100ml", "Facial Cleanser 150ml",
        "Sunscreen Lotion SPF30 100ml", "Lip Gloss Set (4pc)", "Mascara (Waterproof)",
        "Foundation (Medium Tone)", "Setting Spray 100ml", "Makeup Brush Set (12pc)",
        "Nail Polish Set (6 colors)", "Hair Conditioner 400ml", "Shampoo (Sulfate-Free) 400ml",
        "Body Lotion 500ml", "Deodorant Roll-On 50ml", "Perfume 50ml",
        "Face Mask (Clay) 100g", "Exfoliating Scrub 150ml", "Toner 200ml",
        "Eye Cream 30ml", "Hair Gel 250ml", "Edge Control 100ml",
        "Braiding Hair (Pack of 3)", "Wig Cap", "Makeup Remover Wipes (25pc)",
        "Bath Bombs (Set of 6)", "Essential Oil Set (4pc)", "Beard Oil 50ml",
        "Teeth Whitening Kit", "Hair Dryer (Compact)", "Straightening Comb",
    ],
    "Home & Garden": [
        "Bedsheet Set (Queen)", "Throw Pillow (2-Pack)", "Scented Candle (Vanilla)",
        "Wall Clock (Minimalist)", "Photo Frame Set (3pc)", "Door Mat",
        "Shower Curtain", "Kitchen Towels (Pack of 4)", "Cutting Board (Bamboo)",
        "Non-Stick Frying Pan 28cm", "Blender (600W)", "Electric Kettle 1.7L",
        "Storage Containers (Set of 5)", "Laundry Basket", "Ironing Board",
        "Mop & Bucket Set", "Garden Hose 15m", "Plant Pot (Ceramic, Medium)",
        "LED Bulb (Pack of 4)", "Extension Cord 5m", "Curtain Rod Set",
        "Dish Rack", "Trash Can (Pedal, 30L)", "Broom & Dustpan Set",
        "Clothes Drying Rack", "Spice Rack (Rotating)", "Wine Glasses (Set of 4)",
        "Dinner Plate Set (6pc)", "Vacuum Cleaner (Handheld)", "Air Freshener (3-Pack)",
    ],
    "Sports": [
        "Yoga Mat 6mm", "Resistance Bands (Set of 5)", "Jump Rope (Adjustable)",
        "Dumbbell Set 5kg (Pair)", "Water Bottle 750ml", "Gym Gloves",
        "Running Armband", "Foam Roller 45cm", "Sports Towel (Quick Dry)",
        "Fitness Tracker Band", "Pull-Up Bar (Doorframe)", "Kettlebell 8kg",
        "Ab Roller Wheel", "Boxing Gloves 12oz", "Skipping Rope (Speed)",
        "Ankle Weights 2kg (Pair)", "Gym Bag (Duffle)", "Swim Goggles",
        "Tennis Balls (Pack of 3)", "Football (Size 5)", "Basketball (Indoor/Outdoor)",
        "Badminton Racket Set", "Table Tennis Set", "Cycling Gloves",
        "Knee Support Brace", "Wrist Wraps (Pair)", "Protein Shaker 700ml",
        "Exercise Ball 65cm", "Push-Up Board", "Grip Strength Trainer",
    ],
}
