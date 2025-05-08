from pydantic import BaseModel, Field, HttpUrl, validator
from typing import Optional
from datetime import datetime
import re

class Movie(BaseModel):
    film: str = Field(..., min_length=1)
    year: int = Field(..., ge=1878, le=datetime.now().year)
    wikipedia_url: HttpUrl
    oscar_winner: bool
    budget_raw: str
    budget_usd: int = Field(ge=0)

    @validator("film")
    def validate_file_name(cls, v):
        if not v.strip():
            raise ValueError("film cannot be empty or just whitespace.")
        return v.strip()
    
    @validator("budget_raw", pre=True)
    def validate_budget_raw_format(cls, v):
        if not v or not isinstance(v, str):
            return "0"
        if v.lower().strip() in ["unknown", "n/a"]:
            return "0"
        return v.strip()
    
    @validator("budget_usd")
    def validate_usd_budget(cls, v):
        if v > 10_000_000_000: # No film had this budget
            raise ValueError(f"budget_usd too large: {v}")