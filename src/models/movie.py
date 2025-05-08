from pydantic import BaseModel, Field, HttpUrl, ConfigDict, field_validator
from typing import Optional
from datetime import datetime


class Movie(BaseModel):
    """
    Domain model for a film, with metadata and cleaned budget fields.
    """

    film: str = Field(..., min_length=1, description="Non-blank film title")
    year: int = Field(
        ...,
        ge=1878,
        le=datetime.now().year,
        description="Release year between first motion picture (1878) and current year",
    )
    wikipedia_url: HttpUrl = Field(..., description="URL to the films Wikipedia page")
    oscar_winner: bool = Field(
        ..., description="Flag indicating whether the film won an Oscar"
    )
    budget_raw: Optional[str] = Field(
        None, description="Original budget string as scraped"
    )
    budget_usd: int = Field(
        ...,
        ge=0,
        le=10_000_000_000,
        description="Budget converted to USD; must be between 0 and 10 billion",
    )
    budget_updated: int = Field(
        ...,
        ge=0,
        le=10_000_000_000,
        description="Budget converted to USD and adjusted for inflation; must be between 0 and 10 billion",
    )

    @field_validator("film", mode="before")
    @classmethod
    def validate_film_title(cls, v: str) -> str:
        """
        Strip surrounding whitespace and ensure the title is not empty.

        Raises:
            ValueError: If the stripped title is an empty string.
        """
        if not v.strip():
            raise ValueError("film cannot be empty or just whitespace.")
        return v.strip()

    model_config = ConfigDict(extra="forbid", validate_default=True)
