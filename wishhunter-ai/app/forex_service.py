"""Currency conversion service for WishHunter AI using the Frankfurter public API.

Listed in public-apis (Currency Exchange).
Provides real-time foreign currency conversion between USD/EUR/GBP/etc. and INR
for international price parity comparisons.
"""

import json
import os
import urllib.request
from typing import Any


def fetch_currency_conversion(
    amount: float, from_currency: str = "USD", to_currency: str = "INR"
) -> dict[str, Any]:
    """Convert an international product price to INR using the Frankfurter public API.

    Args:
        amount: Price amount in the source currency (e.g. 799 for $799 USD).
        from_currency: 3-letter source currency code (e.g. 'USD', 'EUR', 'GBP').
        to_currency: 3-letter target currency code (default 'INR').

    Returns:
        Structured dictionary with converted amount, exchange rate, and source date.
    """
    from_curr = from_currency.strip().upper()
    to_curr = to_currency.strip().upper()

    if from_curr == to_curr:
        return {
            "original_amount": amount,
            "from_currency": from_curr,
            "to_currency": to_curr,
            "converted_amount": round(amount, 2),
            "exchange_rate": 1.0,
            "status": "success",
        }

    # Read optional API key from environment variable if configured
    api_key = os.environ.get("EXCHANGE_RATE_API_KEY", "").strip()

    try:
        url = f"https://api.frankfurter.dev/v1/latest?amount={amount}&base={from_curr}&symbols={to_curr}"
        headers = {"User-Agent": "WishHunter-AI/1.0"}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        rates = data.get("rates", {})
        if to_curr not in rates:
            return {
                "error": f"Currency code '{to_curr}' not supported by conversion provider."
            }

        converted_total = rates[to_curr]
        unit_rate = round(converted_total / amount, 4) if amount else 0.0

        return {
            "status": "success",
            "original_amount": amount,
            "from_currency": from_curr,
            "to_currency": to_curr,
            "converted_amount": round(converted_total, 2),
            "exchange_rate": unit_rate,
            "rate_date": data.get("date", ""),
            "provider": "Frankfurter API (European Central Bank Reference)",
        }
    except Exception as e:
        return {
            "error": f"Failed to fetch currency conversion: {str(e)}",
            "status": "failed",
        }
