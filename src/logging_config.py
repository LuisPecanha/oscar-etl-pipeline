import logging.config
import yaml
from pathlib import Path


def setup_logging(
    cfg_path: Path | None = None,
    default_level: int = logging.INFO,
):
    project_root = Path(__file__).parent.parent

    if cfg_path is None:
        cfg_path = project_root / "config" / "logging.yaml"

    if cfg_path.exists():
        with open(cfg_path, "r") as f:
            config = yaml.safe_load(f)

        # fix any file‐handler paths and create directories
        handlers = config.get("handlers", {})
        for h in handlers.values():
            fn = h.get("filename")
            if fn:
                # resolve relative to project_root
                log_file = (project_root / fn).resolve()
                log_file.parent.mkdir(parents=True, exist_ok=True)
                h["filename"] = str(log_file)

        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)
