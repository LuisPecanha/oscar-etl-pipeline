from pathlib import Path
from pydantic import BaseModel
import yaml

PROJECT_ROOT = Path(__file__).parent.parent


class Settings(BaseModel):
    api_base_url: str
    output_dir: str


def load_settings(cfg_path: Path | None = None) -> Settings:
    """
    Load settings.yaml (defaults to PROJECT_ROOT/config/settings.yaml)
    """
    if cfg_path is None:
        cfg_path = PROJECT_ROOT / "config" / "settings.yaml"
    with cfg_path.open("r") as f:
        data = yaml.safe_load(f)
    return Settings(**data)
