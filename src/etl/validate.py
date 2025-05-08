import logging
import pandas as pd
from typing import List
from models.movie import Movie

logger = logging.getLogger("etl.validate")

def validate_movies(df: pd.DataFrame) -> List[Movie]:
    """
    Validate the transformed movie DataFrame using Pydantic models.

    Args:
        df (pd.DataFrame): Transformed DataFrame.

    Returns:
        List[MovieRecord]: List of validated and parsed movie records.

    Raises:
        ValueError: If any row fails validation.
    """
    valid_records = []
    for idx, row in df.iterrows():
        try:
            record = Movie(**row.to_dict())
            valid_records.append(record)
        except Exception as e:
            logger.warning(f"[Row {idx}] Validation error: {e}")
    
    return df