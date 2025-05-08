from __future__ import annotations
import logging
import pandas as pd
from time import perf_counter

from .extract import fetch_oscar_data, enrich_with_film_budget
from .transform import clean_budget_column, clean_year_column, add_inflation_adjusted_budget
from .validate import validate_movies
from .load import to_csv

logger = logging.getLogger("etl")

def extract() -> pd.DataFrame:
    """
    Extract data from the API and enrich it with film budget information.
    
    Returns:
        pd.DataFrame: The enriched DataFrame containing Oscar data along with budget.
    """
    start = perf_counter()
    df_raw = fetch_oscar_data()
    df_full = enrich_with_film_budget(df_raw, max_workers=20)
    logger.info(f"Extract stage completed in {perf_counter() - start:.2f} seconds.")
    return df_full

def transform(df: pd.DataFrame) -> pd.DataFrame:
    """
    Transform the DataFrame by cleaning the budget and year columns.
    
    Args:
        df (pd.DataFrame): The DataFrame to transform.
    
    Returns:
        pd.DataFrame: The transformed DataFrame.
    """
    start = perf_counter()
    df_cleaned = clean_budget_column(df)
    df_cleaned = clean_year_column(df_cleaned)
    df_cleaned = add_inflation_adjusted_budget(df_cleaned)
    logger.info(f"Transform stage completed in {perf_counter() - start:.2f} seconds.")
    return df_cleaned

def validate(df: pd.DataFrame) -> pd.DataFrame:
    """
    Validate the DataFrame to ensure it meets the required schema.

    Args:
        df (pd.DataFrame): The DataFrame to validate.
    Returns:
        pd.DataFrame: The validated DataFrame.
    """
    start = perf_counter()
    validated_df = validate_movies(df)
    logger.info(f"Validation stage completed in {perf_counter() - start:.2f} seconds.")
    return validated_df

def load(df: pd.DataFrame) -> str:
    """
    Load the DataFrame to a CSV file.
    
    Args:
        df (pd.DataFrame): The DataFrame to load.
    
    Returns:
        str: The path to the saved CSV file.
    """
    start = perf_counter()
    output_path = to_csv(df)
    return output_path

__all__ = ["extract", "transform", "validate", "load"]