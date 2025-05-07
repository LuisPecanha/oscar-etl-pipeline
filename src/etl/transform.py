import pandas as pd
import re
import logging
from currency import get_exchange_rates

logger = logging.getLogger("etl.transform")

UNIT_MULTIPLIERS = {
    "million": 1_000_000,
    "billion": 1_000_000_000,
    "thousand": 1_000,
}


def parse_budget_value(value: str, conversion_rates: dict) -> int:
    """
    Parse a film budget string into a full-integer USD amount.

    Args:
        value (str): The budget value string.
        conversion_rates (dict): A dictionary of currency conversion rates.

    Returns:
        int: The budget value in USD.
    """
    try:
        if pd.isna(value) or not str(value).strip():
            return 0

        s = str(value).strip()
        # 1) strip out […], (…), and '+'
        s = re.sub(r"\[.*?\]", "", s)
        s = re.sub(r"\(.*?\)", "", s)
        s = s.replace("+", "").strip().lower()

        # 2) “or” ⇒ split and recurse, then take min
        if re.search(r"\bor\b", s):
            parts = re.split(r"\bor\b", s)
            vals = [parse_budget_value(p, conversion_rates) for p in parts]
            vals = [v for v in vals if v > 0]
            return int(min(vals)) if vals else 0

        # 3) range (e.g. “16.5-18 million”) ⇒ take lower bound
        if re.search(r"[\d,.]+\s*[–-]\s*[\d,.]+", s):
            lower = re.split(r"[\u2013\u2014\-]", s, maxsplit=1)[0].strip()
            m = re.match(r"(us\$|\$|€|£|₤)?\s*([\d.]+)", lower, flags=re.IGNORECASE)
            if not m:
                return 0
            sym, num = m.groups()
            amount = float(num)
            # grab the unit from the full string
            um = re.search(r"(million|billion|thousand)", s, flags=re.IGNORECASE)
            unit = um.group(0).lower() if um else None
            unit_mul = UNIT_MULTIPLIERS.get(unit, 1)
            fx = conversion_rates.get((sym or "$").lower(), 0)
            return int(amount * unit_mul * fx)

        # 4) otherwise find all (currency, number, unit) and sum
        pattern = r"(us\$|\$|€|£|₤)?\s*([\d,]+(?:\.\d+)?)\s*(million|billion|thousand)?"
        matches = re.findall(pattern, s, flags=re.IGNORECASE)
        total = 0
        for sym, num, unit in matches:
            amt = float(num.replace(",", ""))
            unit_mul = UNIT_MULTIPLIERS.get(unit.lower() if unit else None, 1)
            fx = conversion_rates.get((sym or "$").lower(), 0)
            total += amt * unit_mul * fx

        return int(total)
    
    except Exception as e:
        logger.warning(f"Failed to parse value '{value}': {e}")
        return 0


def clean_budget_column(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean the budget column in the DataFrame.

    Args:
        df (pd.DataFrame): The DataFrame containing the budget column.

    Returns:
        pd.DataFrame: The DataFrame with the cleaned budget column.
    """
    logger.info("Processing budget column...")
    usd_exchange_rates = get_exchange_rates()

    df["budget_cleaned"] = df["budget"].apply(
        lambda v: parse_budget_value(v, usd_exchange_rates)
    )
    return df


def clean_year_column(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean the year column in the DataFrame.

    Args:
        df (pd.DataFrame): The DataFrame containing the year column.

    Returns:
        pd.DataFrame: The DataFrame with the cleaned year column.
    """
    logger.info("Processing year column...")
    df["year"] = df["year"].astype(str).str.extract(r"(\d{4})").astype("Int64")
    return df
