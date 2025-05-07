import requests
import logging

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


def get_exchange_rates(base_currency: str = "USD") -> dict:
    """
    Fetch live conversion rates from Frankfurter.app (no API key required).
    Falls back to USD_EXCHANGE_RATES on any error.
    Returns a dict mapping currency symbols (e.g. '€', '£') to USD-per-unit.
    """
    url = f"https://api.frankfurter.app/latest?from={base_currency}"
    try:
        logger.info("Fetching rates from Frankfurter.app…")
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
        data = resp.json()
        rates_json = data.get("rates", {})

        rates = {}
        for sym, code in SYMBOL_TO_CODE.items():
            api_rate = rates_json.get(code)
            if api_rate and api_rate > 0:
                # Frankfurter: 1 USD = api_rate × CODE
                # We need: 1 CODE = USD_per_CODE → invert
                rates[sym] = 1.0 / api_rate
            else:
                rates[sym] = USD_EXCHANGE_RATES[sym]

        logger.debug(f"Built rates: {rates}")
        return rates

    except Exception as e:
        logger.warning(f"Frankfurter.app failed ({e}); falling back.")
        return USD_EXCHANGE_RATES.copy()
