# ruff: noqa
# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.apps import App
from google.adk.models import Gemini
from google.adk.tools import ToolContext
from google.adk.tools.preload_memory_tool import PreloadMemoryTool
from google.genai import types

from a2ui.basic_catalog.provider import BasicCatalog
from a2ui.schema.manager import A2uiSchemaManager

from app.a2ui_utils import a2ui_callback

from app.firestore_service import (
    evaluate_buy_or_wait_deal,
    get_product_by_id,
    get_user_wishlist,
    save_user_wishlist_item,
    search_catalog_products,
    update_catalog_product_price,
)
from app.forex_service import fetch_currency_conversion
from app.image_service import generate_item_image_bytes
from app.maps_service import geocode_address_to_coords, search_nearby_places_by_type
from app.sandbox_service import get_sandbox_code_executor, run_python_in_sandbox


MODEL = "gemini-3.8-flash"


def search_products(
    query: str = "", category: str = "", pincode: str = ""
) -> list[dict]:
    """Search products in the Firestore catalog by keyword or category, and verify PIN code delivery.

    Args:
        query: Search term (e.g., 'OnePlus', 'iPhone', 'MacBook', 'headphones').
        category: Category filter (e.g., 'Smartphones', 'Laptops', 'Audio').
        pincode: 6-digit Indian PIN code to check delivery eligibility (e.g. '560001').

    Returns:
        List of matching products with current pricing, retailer availability, and delivery status.
    """
    return search_catalog_products(query=query, category=category, pincode=pincode)


def get_product_details(product_id: str) -> dict:
    """Retrieve full product information, retailer offers, and historical benchmarks from Firestore.

    Args:
        product_id: Unique product identifier (e.g., 'oneplus-12r', 'iphone-15', 'macbook-air-m2').

    Returns:
        Dict containing MRP, current price, 90-day median, historical low, and retailer offers.
    """
    return get_product_by_id(product_id=product_id)


def get_wishlist(user_id: str = "default_user") -> list[dict]:
    """Fetch active tracked items and price targets from the user's Firestore wishlist.

    Args:
        user_id: User identifier (defaults to 'default_user').

    Returns:
        List of tracked wishlist items with target prices and urgency horizons.
    """
    return get_user_wishlist(user_id=user_id)


def save_to_wishlist(
    product_id: str,
    target_price: float,
    urgency_days: int = 14,
    notes: str = "",
    user_id: str = "default_user",
) -> dict:
    """Save or update a tracked item with a target price and urgency in the Firestore wishlist.

    Args:
        product_id: Product ID to track (e.g., 'oneplus-12r').
        target_price: Target alert price in INR (e.g., 40000).
        urgency_days: How many days the user can wait (e.g., 14 for two weeks).
        notes: User preferences or notes (e.g., 'Looking for HDFC card discount').
        user_id: User identifier (defaults to 'default_user').

    Returns:
        Confirmation status and saved wishlist details.
    """
    return save_user_wishlist_item(
        product_id=product_id,
        target_price=target_price,
        urgency_days=urgency_days,
        notes=notes,
        user_id=user_id,
    )


def update_product_price(
    product_id: str, new_price: float, retailer: str = "Amazon.in"
) -> dict:
    """Update a product's live price in Firestore and recalculate historical low if applicable.

    Args:
        product_id: Product ID (e.g., 'oneplus-12r').
        new_price: New observed price in INR.
        retailer: Retailer name where the new price was found (e.g., 'Amazon.in', 'Flipkart').

    Returns:
        Status dict with old price, new price, and updated historical low.
    """
    return update_catalog_product_price(
        product_id=product_id, new_price=new_price, retailer=retailer
    )


def evaluate_buy_or_wait(
    product_id: str, urgency_days: int = 14, bank_card: str = ""
) -> dict:
    """Analyze historical price benchmarks, bank offers, and user urgency to decide whether to BUY NOW or WAIT.

    Args:
        product_id: Unique product identifier (e.g., 'oneplus-12r', 'iphone-15', 'macbook-air-m2').
        urgency_days: Number of days the user can wait before needing the product (default 14).
        bank_card: Optional bank name to check for instant card discounts (e.g., 'HDFC', 'ICICI', 'SBI').

    Returns:
        Dict with recommendation ('BUY NOW', 'WAIT', or 'INSUFFICIENT EVIDENCE'), effective price, confidence, and reasoning.
    """
    return evaluate_buy_or_wait_deal(
        product_id=product_id, urgency_days=urgency_days, bank_card=bank_card
    )


def convert_currency(
    amount: float, from_currency: str = "USD", to_currency: str = "INR"
) -> dict:
    """Convert international product prices to Indian Rupees (INR) using live exchange rates.

    Use this when comparing prices of imported gadgets, US or European retail prices (USD, EUR, GBP),
    or checking global price parity for electronics against Indian retail prices.

    Args:
        amount: The price amount in the source currency (e.g. 799 for $799 USD).
        from_currency: 3-letter currency code (e.g., 'USD', 'EUR', 'GBP').
        to_currency: 3-letter target currency code (default 'INR').

    Returns:
        Dict containing converted amount in INR, unit exchange rate, and rate date.
    """
    return fetch_currency_conversion(
        amount=amount, from_currency=from_currency, to_currency=to_currency
    )


def geocode_address(address: str) -> dict:
    """Turn an address, neighborhood, city, or Indian PIN code into coordinates using Google Maps Geocoding API.

    Args:
        address: The address string, neighborhood, or PIN code (e.g., 'Indiranagar Bengaluru', '560001').

    Returns:
        Dict with name, formatted address, and location coordinates (latitude, longitude).
    """
    return geocode_address_to_coords(address=address)


def find_nearby_places(
    latitude: float,
    longitude: float,
    place_type: str = "electronics_store",
    radius_meters: float = 5000.0,
) -> list[dict]:
    """Find nearby places of a given type using Google Maps Places API (New) searchNearby REST endpoint.

    Args:
        latitude: Latitude coordinate of the search center.
        longitude: Longitude coordinate of the search center.
        place_type: Type of place to search for (e.g., 'electronics_store', 'shopping_mall', 'store').
        radius_meters: Search radius in meters (default 5000.0 / 5km).

    Returns:
        List of nearby places with key fields: name, address, and location coordinates.
    """
    return search_nearby_places_by_type(
        latitude=latitude,
        longitude=longitude,
        place_type=place_type,
        radius_meters=radius_meters,
    )


async def generate_product_image(
    item_name: str,
    style_prompt: str = "",
    tool_context: ToolContext = None,
) -> dict:
    """Generate an image for an item or gadget setup using gemini-3.1-flash-lite-image in the global region.

    Saves the image with tool_context.save_artifact (showing in Playground's Artifacts panel)
    and uploads the image bytes directly to public Cloud Storage, returning the public HTTPS URL.

    Args:
        item_name: Name of the item or gadget (e.g., 'OnePlus 12R', 'iPhone 15', 'MacBook Air M2').
        style_prompt: Optional styling or visual guidance (e.g., 'sleek desk setup', 'minimalist aesthetic').

    Returns:
        Dict with public_image_url, artifact_filename, and status.
    """
    image_bytes, mime_type, filename, public_url = generate_item_image_bytes(
        item_name=item_name, style_prompt=style_prompt
    )

    if tool_context is not None:
        try:
            artifact_part = types.Part.from_bytes(data=image_bytes, mime_type=mime_type)
            await tool_context.save_artifact(filename=filename, artifact=artifact_part)
        except Exception:
            pass

    return {
        "status": "success",
        "item_name": item_name,
        "public_image_url": public_url,
        "artifact_filename": filename,
        "message": f"Generated image for '{item_name}', saved as artifact '{filename}', and uploaded to public Cloud Storage.",
    }


def execute_python_code(python_code: str) -> dict:
    """Execute Python code safely inside the Vertex AI Agent Engine sandbox.

    Use this for exact financial calculations, EMI breakdowns, discounts, price trend analysis,
    GST computations, and verifying savings figures with deterministic code execution.

    Args:
        python_code: Python code string to execute. Always use print() to output results.

    Returns:
        Dict with stdout, stderr, and execution status.
    """
    return run_python_in_sandbox(python_code=python_code)


async def generate_memories_callback(callback_context: CallbackContext):
    """After each turn, send the session events to Memory Bank for extraction."""
    await callback_context.add_session_to_memory()
    return None


schema_manager = A2uiSchemaManager(
    version="0.8",
    catalogs=[BasicCatalog.get_config("0.8")],
)

role_description = (
    "You are WishHunter AI, an intelligent personal shopping advisor for Indian consumers.\n"
    "You remember the user's stated preferences, budget constraints, preferred brands, PIN codes/delivery addresses, "
    "and facts across previous conversations, using them to personalize every recommendation.\n"
    "Crucially, you strictly remember and track all user allergies, sensitivities, and dietary restrictions "
    "(e.g., gluten, peanuts, dairy, lactose, nickel, latex, specific cosmetics/chemicals) across conversations, "
    "always acknowledging them and proactively warning about or filtering out allergen risks in products.\n\n"
    "Your mission is to help users make confident purchasing decisions by:\n"
    "1. Searching the product catalog in Firestore across retailers like Amazon.in and Flipkart.\n"
    "2. Checking delivery eligibility and SLAs for 6-digit Indian PIN codes.\n"
    "3. Comparing current prices against historical benchmarks (MRP, 90-day median, historical low).\n"
    "4. Calling evaluate_buy_or_wait to provide grounded BUY NOW vs. WAIT advice based on price trends, bank discounts, and user urgency.\n"
    "5. Managing persistent wishlist tracking and target price alerts in Firestore.\n"
    "6. Using convert_currency to evaluate global price parity when users compare international prices (USD, EUR, GBP) to Indian Rupees (INR).\n"
    "7. Locating physical retail stores and pickup points using geocode_address and find_nearby_places (Google Maps Geocoding & Places New APIs).\n"
    "8. Generating realistic visual product mockups and dream setups with generate_product_image (gemini-3.1-flash-lite-image) and returning the public Cloud Storage image URL.\n"
    "9. Safely running Python in the Agent Engine sandbox (via execute_python_code or sandbox code execution) to calculate precise financial figures, EMI schedules, or custom formulas.\n\n"
    "Always use your tools to fetch verified product facts, live currency rates, location data, image URLs, and wishlist records."
)

instruction = schema_manager.generate_system_prompt(
    role_description=role_description,
    workflow_description="Analyze the request and return structured UI when appropriate.",
    ui_description=(
        "Keep every surface tiny and flat: ONE Card > ONE Column > a few Text rows. "
        "Never nest a Card inside a Card. "
        "Use ONLY these components: Card, Column, Row, Text, and Image. Do not use "
        "Table or Heading (unsupported), or Buttons, actions, or forms (they do "
        "nothing in adk web). "
        "You may include one Image component, but only when you have a public https "
        "URL for the image (for example the URL an image tool returns after uploading "
        "to a public bucket). Set the Image url to that exact https link, for example "
        "{\"Image\": {\"url\": {\"literalString\": \"https://...\"}}}. Never point an "
        "Image at a bare filename, an artifact name, or a non-http(s) path. If you do "
        "not have a public URL, add a short Text line noting the image instead. "
        "No markdown in text; use the usageHint property ('h1', 'h2', 'body') for "
        "headings and emphasis. "
        "Output ONLY the raw A2UI JSON array — no prose, and never wrap it in "
        "<a2a_datapart_json> tags or 'kind'/'data'/'metadata' objects."
    ),
    include_schema=True,
    include_examples=True,
)


root_agent = Agent(
    name="root_agent",
    model=Gemini(
        model=MODEL,
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    code_executor=get_sandbox_code_executor(),
    instruction=instruction,
    tools=[
        PreloadMemoryTool(),
        search_products,
        get_product_details,
        evaluate_buy_or_wait,
        get_wishlist,
        save_to_wishlist,
        update_product_price,
        convert_currency,
        geocode_address,
        find_nearby_places,
        generate_product_image,
        execute_python_code,
    ],
    after_model_callback=a2ui_callback,
    after_agent_callback=generate_memories_callback,
)

app = App(
    root_agent=root_agent,
    name="app",
)
