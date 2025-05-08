import os
import yaml
import requests
import pandas as pd
import logging
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import quote, unquote
from http_client import SESSION
from config import load_settings
from requests.exceptions import (
    HTTPError,
    Timeout,
    ConnectionError,
    RequestException,
)

logger = logging.getLogger("etl.extract")


def clean_url(url: str) -> str:
    """
    Clean the URL.

    Args:
        url (str): The URL to clean.

    Returns:
        str: The cleaned URL.
    """
    decoded = unquote(url)
    return quote(decoded, safe=":/()_")


def fetch_oscar_data() -> pd.DataFrame:
    """
    Fetch the Oscar data from the API.
    """
    logger.debug("Fetching Oscar data from API...")
    config = load_settings()
    base_url = config.api_base_url

    try:
        response = SESSION.get(base_url, timeout=10)
        response.raise_for_status()
        data = response.json()
    except HTTPError as e:
        logger.error(f"HTTP error {e} for URL {base_url}")
        return pd.DataFrame()
    except Timeout:
        logger.error(f"Timeout error for URL {base_url}")
        return pd.DataFrame()
    except ConnectionError:
        logger.error(f"Connection error for URL {base_url}")
        return pd.DataFrame()
    except RequestException as e:
        logger.error(f"Request error for URL {base_url}")
        return pd.DataFrame()
    except ValueError as e:
        logger.error(f"Invalid JSON for URL {base_url}")
        return pd.DataFrame()

    records = []
    for entry in data["results"]:
        year = entry["year"]
        for film in entry["films"]:
            film_data = {
                "film": film.get("Film"),
                "year": year,
                "wikipedia_url": film.get("Wiki URL"),
                "oscar_winner": film.get("Winner"),
                "detail_url": film.get("Detail URL"),
            }
            records.append(film_data)

    df = pd.DataFrame(records)
    return df


def fetch_budget(detail_url: str) -> dict:
    """
    Fetch the filme budget from the given URL, with retries/backoff

    Args:
        detail_url (str): The URL to fetch film budget from.

    Returns:
        dict: The film budget.
    """
    cleaned_url = clean_url(detail_url)
    try:
        response = SESSION.get(cleaned_url, timeout=10)
        response.raise_for_status()
        data = response.json()
        return {"budget": data.get("Budget")}
    except requests.HTTPError as e:
        code = e.response.status_code
        logger.warning(f"HTTP error {code} for URL {detail_url}")
    except Timeout:
        logger.warning(f"Timeout error for URL {detail_url}")
    except ConnectionError:
        logger.warning(f"Connection error for URL {detail_url}")
    except RequestException as e:
        logger.warning(f"Request error {e} for URL {detail_url}")
    except ValueError as e:
        logger.warning(f"Value error {e} for URL {detail_url}")
    return {"budget": None}


def enrich_with_film_budget(df: pd.DataFrame, max_workers: int = 20) -> pd.DataFrame:
    """
    Enrich the film data with its budget from the API.

    Args:
        df (pd.DataFrame): The DataFrame containing film data.
        max_workers (int): The maximum number of threads to use for fetching details.

    Returns:
        pd.DataFrame: The enriched DataFrame with film budget included.
    """

    urls = df["detail_url"].tolist()
    results = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = list(
            tqdm(
                executor.map(fetch_budget, urls),
                total=len(urls),
                desc="Fetching film details",
                unit="film",
            )
        )

    detail_df = pd.DataFrame(results)
    df = df.drop(columns=["detail_url"]).reset_index(drop=True)
    detail_df = detail_df.reset_index(drop=True)

    return pd.concat([df, detail_df], axis=1)
