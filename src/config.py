from pydantic import BaseModel
import yaml


class Settings(BaseModel):
    api_base_url: str
    output_dir: str


def load_config(path="config/settings.yaml") -> Settings:
    with open(path, "r") as f:
        config = yaml.safe_load(f)
    return Settings(**config)
