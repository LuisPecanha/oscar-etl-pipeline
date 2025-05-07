import os
import yaml
import requests
import pandas as pd
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed


def load_config():
    """
    Load the configuration file.
    """
    with open(os.path.join("../config", "settings.yaml")) as file:
        return yaml.safe_load(file)


def fetch_oscar_data() -> pd.DataFrame:
    """
    Fetch the Oscar data from the API.
    """
    config = load_config()
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


def obtain_film_details(df: pd.DataFrame) -> pd.DataFrame:
    """

    Args:
        df (_type_): _description_
    """
    details = []

    for url in tqdm(df["Detail URL"], desc="Fetching film details"):
        try:
            response = requests.get(url)
            response.raise_for_status()
            details.append(response.json())
        except Exception as e:
            details.append({})

    return pd.concat([df.reset_index(drop=True), pd.DataFrame(details)], axis=1)
