"""Seed script for WishHunter AI Firestore database.

Populates initial product catalog and historical benchmarks into Firestore.
"""

from datetime import datetime, timezone
from google.cloud import firestore

# CRITICAL: Hardcode project ID as a string.
# Do NOT read from google.auth.default() or GOOGLE_CLOUD_PROJECT to prevent project number resolution issues on Agent Platform.
PROJECT_ID = "qwiklabs-gcp-04-28d6773dbc5b"


def get_db():
    return firestore.Client(project=PROJECT_ID)


SEEDED_PRODUCTS = [
    {
        "product_id": "oneplus-12r",
        "name": "OnePlus 12R 5G (Cool Blue, 16GB RAM, 256GB Storage)",
        "category": "Smartphones",
        "brand": "OnePlus",
        "mrp": 45999,
        "current_price": 42999,
        "historical_low": 38999,
        "median_90d": 43500,
        "rating": 4.5,
        "reviews_count": 8920,
        "eligible_pincodes": ["560001", "110001", "400001", "500001", "208001", "600001"],
        "retailers": [
            {
                "retailer": "Amazon.in",
                "price": 42999,
                "in_stock": True,
                "delivery_sla_days": 2,
                "bank_offers": "₹2,000 instant discount on HDFC Credit Cards; 5% cashback on Amazon Pay ICICI Card",
                "url": "https://www.amazon.in/dp/B0CS51R5M8",
            },
            {
                "retailer": "Flipkart",
                "price": 43499,
                "in_stock": True,
                "delivery_sla_days": 3,
                "bank_offers": "₹1,500 off on Axis Bank Flipkart Credit Card",
                "url": "https://www.flipkart.com/oneplus-12r-5g",
            },
        ],
        "specifications": {
            "display": "6.78-inch 1.5K LTPO4 AMOLED 120Hz",
            "processor": "Snapdragon 8 Gen 2",
            "battery": "5500 mAh with 100W SUPERVOOC charging",
            "main_camera": "50MP Sony IMX890 with OIS",
        },
        "updated_at": datetime.now(timezone.utc).isoformat(),
    },
    {
        "product_id": "iphone-15",
        "name": "Apple iPhone 15 (Black, 128GB)",
        "category": "Smartphones",
        "brand": "Apple",
        "mrp": 79900,
        "current_price": 65999,
        "historical_low": 58999,
        "median_90d": 69900,
        "rating": 4.6,
        "reviews_count": 14200,
        "eligible_pincodes": ["560001", "110001", "400001", "500001", "208001", "600001", "700001"],
        "retailers": [
            {
                "retailer": "Amazon.in",
                "price": 66499,
                "in_stock": True,
                "delivery_sla_days": 2,
                "bank_offers": "₹4,000 instant discount on SBI and ICICI Credit Cards",
                "url": "https://www.amazon.in/dp/B0CHX1W1XY",
            },
            {
                "retailer": "Flipkart",
                "price": 65999,
                "in_stock": True,
                "delivery_sla_days": 2,
                "bank_offers": "₹4,000 instant discount on HDFC Bank Cards",
                "url": "https://www.flipkart.com/apple-iphone-15-black-128-gb",
            },
        ],
        "specifications": {
            "display": "6.1-inch Super Retina XDR OLED",
            "processor": "A16 Bionic chip",
            "camera": "48MP Main + 12MP Ultra Wide with 2x Telephoto",
            "port": "USB-C",
        },
        "updated_at": datetime.now(timezone.utc).isoformat(),
    },
    {
        "product_id": "macbook-air-m2",
        "name": "Apple MacBook Air M2 (13.6-inch, 16GB Unified Memory, 256GB SSD, Midnight)",
        "category": "Laptops",
        "brand": "Apple",
        "mrp": 99900,
        "current_price": 88990,
        "historical_low": 81990,
        "median_90d": 92000,
        "rating": 4.7,
        "reviews_count": 3100,
        "eligible_pincodes": ["560001", "110001", "400001", "500001", "208001"],
        "retailers": [
            {
                "retailer": "Amazon.in",
                "price": 88990,
                "in_stock": True,
                "delivery_sla_days": 1,
                "bank_offers": "₹5,000 instant discount on HDFC Bank Credit Cards",
                "url": "https://www.amazon.in/dp/B0B3C4Y1XY",
            },
            {
                "retailer": "Flipkart",
                "price": 89990,
                "in_stock": True,
                "delivery_sla_days": 3,
                "bank_offers": "₹3,500 off on ICICI Bank Cards",
                "url": "https://www.flipkart.com/apple-macbook-air-m2",
            },
        ],
        "specifications": {
            "chip": "Apple M2 with 8-core CPU and 8-core GPU",
            "memory": "16GB Unified Memory",
            "storage": "256GB SSD",
            "battery_life": "Up to 18 hours",
        },
        "updated_at": datetime.now(timezone.utc).isoformat(),
    },
    {
        "product_id": "sony-wh1000xm5",
        "name": "Sony WH-1000XM5 Wireless Industry Leading Noise Canceling Headphones (Black)",
        "category": "Audio",
        "brand": "Sony",
        "mrp": 34990,
        "current_price": 26990,
        "historical_low": 24990,
        "median_90d": 28990,
        "rating": 4.6,
        "reviews_count": 6450,
        "eligible_pincodes": ["560001", "110001", "400001", "500001", "208001", "600001", "700001"],
        "retailers": [
            {
                "retailer": "Amazon.in",
                "price": 26990,
                "in_stock": True,
                "delivery_sla_days": 1,
                "bank_offers": "₹2,000 instant discount on all major bank credit cards",
                "url": "https://www.amazon.in/dp/B09XS7JWHH",
            },
            {
                "retailer": "Flipkart",
                "price": 27490,
                "in_stock": True,
                "delivery_sla_days": 2,
                "bank_offers": "₹1,500 instant discount on Axis Bank Card",
                "url": "https://www.flipkart.com/sony-wh-1000xm5",
            },
        ],
        "specifications": {
            "anc": "Auto NC Optimizer with 8 microphones & 2 processors",
            "battery": "Up to 30 hours with fast charging (3 min = 3 hours)",
            "drivers": "Specially engineered 30mm driver unit",
            "bluetooth": "LDAC, Multipoint connection",
        },
        "updated_at": datetime.now(timezone.utc).isoformat(),
    },
    {
        "product_id": "asus-vivobook-15",
        "name": "ASUS Vivobook 15 (Intel Core i5-1335U 13th Gen, 16GB RAM, 512GB SSD, Quiet Blue)",
        "category": "Laptops",
        "brand": "ASUS",
        "mrp": 69990,
        "current_price": 51990,
        "historical_low": 48990,
        "median_90d": 53500,
        "rating": 4.3,
        "reviews_count": 2840,
        "eligible_pincodes": ["560001", "110001", "400001", "500001", "208001"],
        "retailers": [
            {
                "retailer": "Amazon.in",
                "price": 51990,
                "in_stock": True,
                "delivery_sla_days": 2,
                "bank_offers": "₹1,500 instant bank discount + No cost EMI",
                "url": "https://www.amazon.in/dp/B0C3MBX4Y1",
            },
            {
                "retailer": "Flipkart",
                "price": 52490,
                "in_stock": True,
                "delivery_sla_days": 3,
                "bank_offers": "₹1,250 instant discount on HDFC Cards",
                "url": "https://www.flipkart.com/asus-vivobook-15",
            },
        ],
        "specifications": {
            "processor": "Intel Core i5-1335U (10 cores, up to 4.6 GHz)",
            "memory": "16GB DDR4",
            "storage": "512GB M.2 NVMe PCIe 4.0 SSD",
            "display": "15.6-inch FHD Anti-glare",
        },
        "updated_at": datetime.now(timezone.utc).isoformat(),
    },
]


def seed():
    db = get_db()
    products_col = db.collection("products")
    print(f"Seeding products to Firestore collection 'products' in project '{PROJECT_ID}'...")
    for prod in SEEDED_PRODUCTS:
        doc_ref = products_col.document(prod["product_id"])
        doc_ref.set(prod)
        print(f"  ✓ Seeded product: {prod['product_id']} - {prod['name'][:40]}...")

    # Also seed a sample initial wishlist entry
    wishlist_col = db.collection("wishlist")
    sample_wishlist = {
        "user_id": "default_user",
        "product_id": "oneplus-12r",
        "product_name": "OnePlus 12R 5G (Cool Blue, 16GB/256GB)",
        "target_price": 40000,
        "current_price": 42999,
        "urgency_days": 14,
        "user_pincode": "560001",
        "status": "TRACKING",
        "notes": "Looking for price drop below 40k before trip",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    wishlist_col.document("default_user_oneplus-12r").set(sample_wishlist)
    print("  ✓ Seeded initial sample wishlist item for 'default_user'")
    print("Seeding complete!")


if __name__ == "__main__":
    seed()
