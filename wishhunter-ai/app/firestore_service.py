"""Firestore service for WishHunter AI.

Handles database operations for the product catalog and user wishlist.
"""

from datetime import datetime, timezone
from typing import Any
from google.cloud import firestore

# CRITICAL: Hardcode project ID as a literal string.
# Do NOT read from google.auth.default() or GOOGLE_CLOUD_PROJECT to prevent
# project number resolution issues on Agent Platform.
PROJECT_ID = "qwiklabs-gcp-04-28d6773dbc5b"

_db_client: firestore.Client | None = None


def get_firestore_client() -> firestore.Client:
    """Returns a singleton Firestore client instance initialized with hardcoded project ID."""
    global _db_client
    if _db_client is None:
        _db_client = firestore.Client(project=PROJECT_ID)
    return _db_client


def search_catalog_products(
    query: str = "", category: str = "", pincode: str = ""
) -> list[dict[str, Any]]:
    """Search products in Firestore catalog matching a query, category, or checking PIN-code eligibility.

    Args:
        query: Optional search keyword (e.g. 'OnePlus', 'iPhone', 'laptop').
        category: Optional category filter (e.g. 'Smartphones', 'Laptops', 'Audio').
        pincode: Optional 6-digit Indian PIN code to check delivery eligibility.

    Returns:
        A list of matching product dictionaries with pricing and delivery information.
    """
    db = get_firestore_client()
    products_ref = db.collection("products")
    docs = products_ref.stream()

    results: list[dict[str, Any]] = []
    q_lower = query.strip().lower()
    cat_lower = category.strip().lower()

    for doc in docs:
        data = doc.to_dict()
        name = data.get("name", "").lower()
        brand = data.get("brand", "").lower()
        prod_cat = data.get("category", "").lower()
        prod_id = data.get("product_id", "").lower()

        # Category check
        if cat_lower and cat_lower not in prod_cat:
            continue

        # Text query check
        if q_lower:
            match = (
                q_lower in name
                or q_lower in brand
                or q_lower in prod_cat
                or q_lower in prod_id
            )
            if not match:
                continue

        # PIN-code delivery check
        pincode_clean = pincode.strip()
        if pincode_clean:
            eligible_pincodes = data.get("eligible_pincodes", [])
            data["pincode_checked"] = pincode_clean
            data["delivery_eligible"] = pincode_clean in eligible_pincodes
            data["delivery_status"] = (
                f"Eligible for fast delivery to {pincode_clean}"
                if pincode_clean in eligible_pincodes
                else f"Standard shipping or limited availability for PIN {pincode_clean}"
            )

        results.append(data)

    return results


def get_product_by_id(product_id: str) -> dict[str, Any]:
    """Retrieve full details for a product by its unique product_id.

    Args:
        product_id: Product identifier (e.g. 'oneplus-12r', 'iphone-15', 'macbook-air-m2').

    Returns:
        Full product dictionary or an error dictionary if not found.
    """
    db = get_firestore_client()
    doc_ref = db.collection("products").document(product_id.strip().lower())
    doc = doc_ref.get()

    if not doc.exists:
        return {
            "error": f"Product with ID '{product_id}' not found in WishHunter catalog."
        }

    return doc.to_dict()


def save_user_wishlist_item(
    product_id: str,
    target_price: float,
    urgency_days: int = 14,
    notes: str = "",
    user_id: str = "default_user",
) -> dict[str, Any]:
    """Save or update a tracked product in the user's Firestore wishlist.

    Args:
        product_id: Product ID to track (e.g. 'oneplus-12r').
        target_price: Target alert price in INR (e.g. 40000).
        urgency_days: User purchase urgency in days (e.g. 14 for 2 weeks).
        notes: User notes or context (e.g. 'Looking for HDFC discount').
        user_id: User identifier (defaults to 'default_user').

    Returns:
        Status dictionary confirming the wishlist item was saved.
    """
    db = get_firestore_client()
    prod_id_clean = product_id.strip().lower()

    # Look up product name & current price
    prod_data = get_product_by_id(prod_id_clean)
    prod_name = prod_data.get("name", prod_id_clean)
    current_price = prod_data.get("current_price", 0)

    doc_id = f"{user_id}_{prod_id_clean}"
    item_data = {
        "user_id": user_id,
        "product_id": prod_id_clean,
        "product_name": prod_name,
        "target_price": target_price,
        "current_price": current_price,
        "urgency_days": urgency_days,
        "notes": notes,
        "status": "TRACKING",
        "price_reached": current_price <= target_price,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }

    db.collection("wishlist").document(doc_id).set(item_data, merge=True)
    return {
        "status": "success",
        "message": f"Successfully tracked '{prod_name}' with target ₹{target_price:,.0f} in wishlist.",
        "item": item_data,
    }


from google.cloud.firestore_v1.base_query import FieldFilter


def get_user_wishlist(user_id: str = "default_user") -> list[dict[str, Any]]:
    """Fetch all active tracked items from the user's Firestore wishlist.

    Args:
        user_id: User identifier (defaults to 'default_user').

    Returns:
        A list of tracked wishlist items.
    """
    db = get_firestore_client()
    docs = db.collection("wishlist").where(filter=FieldFilter("user_id", "==", user_id)).stream()
    items = [doc.to_dict() for doc in docs]
    return items


def update_catalog_product_price(
    product_id: str, new_price: float, retailer: str = "Amazon.in"
) -> dict[str, Any]:
    """Update current price and historical stats for a product in Firestore.

    Args:
        product_id: The product ID (e.g. 'oneplus-12r').
        new_price: The updated price in INR.
        retailer: Retailer name where the new price was spotted.

    Returns:
        Status dictionary with old and new pricing details.
    """
    db = get_firestore_client()
    doc_ref = db.collection("products").document(product_id.strip().lower())
    doc = doc_ref.get()

    if not doc.exists:
        return {"error": f"Product '{product_id}' not found."}

    data = doc.to_dict()
    old_price = data.get("current_price", new_price)
    historical_low = data.get("historical_low", new_price)

    updates: dict[str, Any] = {
        "current_price": new_price,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    if new_price < historical_low:
        updates["historical_low"] = new_price

    # Update retailer price in list
    retailers = data.get("retailers", [])
    for r in retailers:
        if r.get("retailer", "").lower() == retailer.lower():
            r["price"] = new_price
    updates["retailers"] = retailers

    doc_ref.update(updates)

    return {
        "status": "success",
        "product_id": product_id,
        "old_price": old_price,
        "new_price": new_price,
        "new_historical_low": min(historical_low, new_price),
    }


def evaluate_buy_or_wait_deal(
    product_id: str, urgency_days: int = 14, bank_card: str = ""
) -> dict[str, Any]:
    """Deterministically evaluates whether the user should BUY NOW, WAIT, or if there is INSUFFICIENT EVIDENCE.

    Args:
        product_id: Unique product identifier (e.g. 'oneplus-12r').
        urgency_days: Days the user can wait before purchasing (default 14).
        bank_card: Optional bank name for instant discounts (e.g. 'HDFC', 'ICICI', 'SBI', 'Axis').

    Returns:
        Structured verdict dictionary with decision metrics, discount benchmarks, and confidence.
    """
    import re

    prod = get_product_by_id(product_id)
    if "error" in prod:
        return prod

    name = prod.get("name", product_id)
    mrp = float(prod.get("mrp", 0))
    current_price = float(prod.get("current_price", 0))
    historical_low = float(prod.get("historical_low", 0))
    median_90d = float(prod.get("median_90d", 0))
    retailers = prod.get("retailers", [])

    if current_price <= 0 or historical_low <= 0 or median_90d <= 0:
        return {
            "product_id": product_id,
            "product_name": name,
            "verdict": "INSUFFICIENT EVIDENCE",
            "effective_price": current_price,
            "confidence_pct": 40,
            "reason": "Missing sufficient historical pricing observations for this product.",
            "recommended_target_price": current_price,
        }

    # Best base retailer price
    retailer_prices = [float(r["price"]) for r in retailers if "price" in r]
    base_price = min(retailer_prices) if retailer_prices else current_price

    # Check bank card discount
    card_discount = 0.0
    if bank_card:
        card_query = bank_card.strip().lower()
        for r in retailers:
            offers = r.get("bank_offers", "")
            if card_query in offers.lower():
                match = re.search(
                    r"₹?([0-9,]+)\s*(?:instant discount|off)", offers, re.IGNORECASE
                )
                if match:
                    val = float(match.group(1).replace(",", ""))
                    if val > card_discount:
                        card_discount = val
                else:
                    card_discount = min(base_price * 0.10, 2000.0)

    effective_price = max(0.0, base_price - card_discount)

    diff_vs_low_pct = ((effective_price - historical_low) / historical_low) * 100.0
    discount_vs_median_pct = ((median_90d - effective_price) / median_90d) * 100.0

    if diff_vs_low_pct <= 3.0 or discount_vs_median_pct >= 8.0:
        verdict = "BUY NOW"
        confidence = 94
        reason = (
            f"Effective price ₹{effective_price:,.0f} is within 3% of all-time low (₹{historical_low:,.0f}) "
            f"and {discount_vs_median_pct:.1f}% below the 90-day median (₹{median_90d:,.0f}). Excellent value."
        )
    elif urgency_days <= 3:
        verdict = "BUY NOW"
        confidence = 88
        reason = (
            f"User purchase urgency is high ({urgency_days} days). Significant price reductions "
            f"are improbable in this timeframe."
        )
    elif diff_vs_low_pct > 8.0 and urgency_days >= 7:
        verdict = "WAIT"
        confidence = 90
        potential_savings = effective_price - historical_low
        reason = (
            f"Current price ₹{effective_price:,.0f} is {diff_vs_low_pct:.1f}% above historical low (₹{historical_low:,.0f}). "
            f"With {urgency_days} days to wait, holding for the next sale could save up to ₹{potential_savings:,.0f}."
        )
    else:
        verdict = "BUY NOW" if discount_vs_median_pct > 0 else "WAIT"
        confidence = 78
        reason = (
            f"Effective price is ₹{effective_price:,.0f} compared to 90-day median ₹{median_90d:,.0f}."
        )

    return {
        "product_id": product_id,
        "product_name": name,
        "verdict": verdict,
        "effective_price": effective_price,
        "listed_price": base_price,
        "mrp": mrp,
        "historical_low": historical_low,
        "median_90d": median_90d,
        "discount_vs_median_pct": round(discount_vs_median_pct, 1),
        "distance_to_historical_low_pct": round(diff_vs_low_pct, 1),
        "card_discount_applied": card_discount,
        "bank_card_used": bank_card if card_discount > 0 else "None",
        "confidence_pct": confidence,
        "reason": reason,
        "recommended_target_price": historical_low,
    }

