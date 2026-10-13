"""Google Maps Platform services for WishHunter AI.

Integrates Geocoding API and Places API (New) REST endpoints.
API key is securely loaded from GOOGLE_MAPS_API_KEY in .env.
"""

import json
import os
import urllib.parse
import urllib.request
from typing import Any
from dotenv import load_dotenv

load_dotenv()


def _get_api_key() -> str:
    key = os.environ.get("GOOGLE_MAPS_API_KEY", "").strip()
    if not key:
        raise ValueError("GOOGLE_MAPS_API_KEY is not set in environment or .env file.")
    return key


def geocode_address_to_coords(address: str) -> dict[str, Any]:
    """Geocode an address, landmark, or Indian PIN code to coordinates using the Google Maps Geocoding API.

    Args:
        address: The address string, city, or PIN code (e.g. 'MG Road Bengaluru', 'Connaught Place New Delhi', '560001').

    Returns:
        Dict with name/queried address, formatted address, and location (latitude, longitude).
    """
    if not address or not address.strip():
        return {"error": "Address string cannot be empty."}

    api_key = _get_api_key()
    encoded_addr = urllib.parse.quote(address.strip())
    url = f"https://maps.googleapis.com/maps/api/geocode/json?address={encoded_addr}&key={api_key}"

    try:
        req = urllib.request.Request(url, headers={"User-Agent": "WishHunter-AI/1.0"})
        with urllib.request.urlopen(req, timeout=7) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        status = data.get("status")
        if status != "OK" or not data.get("results"):
            return {
                "error": f"Geocoding failed with status '{status}': {data.get('error_message', 'No results found.')}",
                "address": address,
            }

        first_result = data["results"][0]
        geometry = first_result.get("geometry", {}).get("location", {})
        formatted_address = first_result.get("formatted_address", address)

        return {
            "status": "success",
            "name": address,
            "address": formatted_address,
            "location": {
                "latitude": geometry.get("lat"),
                "longitude": geometry.get("lng"),
            },
        }
    except Exception as e:
        return {"error": f"Failed to geocode address: {str(e)}", "address": address}


def search_nearby_places_by_type(
    latitude: float,
    longitude: float,
    place_type: str = "electronics_store",
    radius_meters: float = 5000.0,
    max_results: int = 5,
) -> list[dict[str, Any]]:
    """Search nearby places of a given type using Google Maps Places API (New) searchNearby REST endpoint.

    Args:
        latitude: Latitude of the center point.
        longitude: Longitude of the center point.
        place_type: Place type table value (e.g., 'electronics_store', 'shopping_mall', 'store').
        radius_meters: Radius to search around coordinates in meters (default 5000m / 5km).
        max_results: Maximum number of places to return (default 5).

    Returns:
        List of matching places with key fields: name, address, and location.
    """
    api_key = _get_api_key()
    url = "https://places.googleapis.com/v1/places:searchNearby"

    payload = {
        "includedTypes": [place_type],
        "maxResultCount": min(max(1, max_results), 20),
        "locationRestriction": {
            "circle": {
                "center": {
                    "latitude": float(latitude),
                    "longitude": float(longitude),
                },
                "radius": float(radius_meters),
            }
        },
    }

    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": api_key,
        "X-Goog-FieldMask": "places.displayName,places.formattedAddress,places.location",
        "User-Agent": "WishHunter-AI/1.0",
    }

    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=7) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        raw_places = data.get("places", [])
        results = []
        for p in raw_places:
            results.append({
                "name": p.get("displayName", {}).get("text", "Unknown"),
                "address": p.get("formattedAddress", ""),
                "location": {
                    "latitude": p.get("location", {}).get("latitude"),
                    "longitude": p.get("location", {}).get("longitude"),
                },
            })
        return results
    except Exception as e:
        return [{"error": f"Failed to search nearby places: {str(e)}"}]
