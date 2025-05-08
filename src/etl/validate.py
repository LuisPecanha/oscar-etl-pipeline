import logging
import pandas as pd
from typing import List
from pydantic import ValidationError
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
        ValidationError: If any row fails validation.
    """
    valid_dicts = []
    for idx, rec in enumerate(df.to_dict(orient="records")):
        try:
            m = Movie(**rec)
            valid_dicts.append(m.dict())
        except ValidationError as e:
            logger.warning(
                "Row %d failed validation: %s | record=%s", idx, e.errors(), rec
            )
    return pd.DataFrame(valid_dicts)
