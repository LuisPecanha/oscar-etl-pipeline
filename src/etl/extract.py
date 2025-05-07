import os
import yaml
import requests
import pandas as pd
import logging
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import quote, unquote
from requests.exceptions import (
    HTTPError,
    Timeout,
    ConnectionError,
    RequestException,
)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36"
}

logger = logging.getLogger("etl.extract")

def load_settings():
    """
    Load the settings file.
    """
    with open(os.path.join("../config", "settings.yaml")) as file:
        return yaml.safe_load(file)


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
    base_url = config["api_base_url"]

    response = requests.get(base_url)
    response.raise_for_status()
    data = response.json()

    records = []
    for entry in data["results"]:
        year = entry["year"]
        for film in entry["films"]:
            film_data = film.copy()
            film_data["year"] = year
            records.append(film_data)

    df = pd.DataFrame(records)
    return df


def fetch_detail(detail_url: str) -> dict:
    """
    Fetch film details from the given URL.

    Args:
        detail_url (str): The URL to fetch film details from.

    Returns:
        dict: The film details.
    """
    try:
        cleaned_url = clean_url(detail_url)
        response = requests.get(cleaned_url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        return response.json()
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
    return {}


def enrich_film_data(df: pd.DataFrame, max_workers: int = 20) -> pd.DataFrame:
    """
    Enrich the film data with details from the API.
    Args:
        df (pd.DataFrame): The DataFrame containing film data.
        max_workers (int): The maximum number of threads to use for fetching details.
    Returns:
        pd.DataFrame: The enriched DataFrame with film details.
    """

    urls = df["Detail URL"].tolist()
    results = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_url = {executor.submit(fetch_detail, url): url for url in urls}

        for future in tqdm(
            as_completed(future_to_url), total=len(urls), desc="Fetching details"
        ):
            results.append(future.result())

    detail_df = pd.DataFrame(results)
    return pd.concat(
        [df.reset_index(drop=True), detail_df.reset_index(drop=True)], axis=1
    )
