import requests
import logging
from http_client import SESSION
from functools import lru_cache

logger = logging.getLogger("etl.currency")

# Static fall-back rates (USD per unit of currency)
USD_EXCHANGE_RATES = {
    "$": 1.0,
    "us$": 1.0,
    "€": 1.08,
    "£": 1.25,
    "₤": 0.000558,  # historical Italian lira
}

# Map from symbol to ISO code that the API uses
SYMBOL_TO_CODE = {
    "$": "USD",
    "us$": "USD",
    "€": "EUR",
    "£": "GBP",
    "₤": "ITL",
}


@lru_cache(maxsize=1)
def get_exchange_rates(base_currency: str = "USD") -> dict:
    """
    Fetch live conversion rates from Frankfurter.app (no API key needed).
    Falls back to USD_EXCHANGE_RATES on any error.
    Returns a dict mapping currency symbols (e.g. '€', '£') to USD-per-unit.
    The result is cached so you only hit the API once per process.

    Args:
        base_currency (str): The base currency to convert from. Default is 'USD'.
    Returns:
        dict: A dictionary mapping currency symbols to their conversion rates.
    """
    url = f"https://api.frankfurter.app/latest?from={base_currency}"
    try:
        logger.info("Fetching rates from Frankfurter.app…")
        resp = SESSION.get(url, timeout=5)
        resp.raise_for_status()
        data = resp.json()
        logger.info(f"Response from Frankfurter.app: {data}")
        rates_json = data.get("rates", {})

        rates = {}
        for sym, code in SYMBOL_TO_CODE.items():

            # Default for USD base currency
            if code.upper() == base_currency.upper():
                rates[sym] = USD_EXCHANGE_RATES[sym]
                continue

            api_rate = rates_json.get(code)
            if api_rate and api_rate > 0:
                # Frankfurter: 1 USD = api_rate × CODE
                # We need: 1 CODE = USD_per_CODE → invert
                rates[sym] = 1.0 / api_rate
            else:
                rates[sym] = USD_EXCHANGE_RATES[sym]
                logger.warning(
                    f"Frankfurter.app returned invalid rate for {code} ({api_rate}); using fall-back rate."
                )

        logger.info(f"{rates}")

        return rates

    except requests.RequestException as e:
        logger.error(f"HTTP  error fetching rates: {e}; falling back.")
    except ValueError as e:
        logger.error(f"Error parsing JSON: {e}; falling back.")
    except Exception as e:
        logger.error(f"Unexpected error in get_exchange_rates: {e}; falling back.")
        return USD_EXCHANGE_RATES.copy()
