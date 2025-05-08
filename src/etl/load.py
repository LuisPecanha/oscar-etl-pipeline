from datetime import datetime
from pathlib import Path
from typing import Union
from tempfile import NamedTemporaryFile
from tenacity import retry, stop_after_attempt, wait_exponential
import logging, time, shutil
import pandas as pd

ALLOWED_COMPRESSIONS = {"gzip", "bz2", "zip", "xz"}

logger = logging.getLogger("etl.load")

# Helpers


def _project_root() -> Path:
    """
    Get the project root directory.
    """
    return Path(__file__).resolve().parents[2]


def _default_output_dir() -> Path:
    """
    Get the default output directory.
    """
    return _project_root() / "data" / "processed"


# retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
def _atomic_write(df, tmp_path, final_path, **to_csv_kwargs):
    """
    Write the DataFrame to a temporary file and then rename it to the final path.
    This ensures that the final file is only created if the write is successful.
    """
    df.to_csv(tmp_path, **to_csv_kwargs)
    Path(tmp_path).replace(final_path)


def to_csv(
    df: pd.DataFrame,
    output_dir: str | Path | None = None,
    fname_prefix: str = "oscar_movies_cleaned",
    include_index: bool = False,
    compression: str | None = None,
) -> Path:
    """
    Write `df` to a timestamped CSV inside *data/processed*.

    Args
    ----
    df : pd.DataFrame
        The cleaned, validated dataframe.
    output_dir : str | Path | None
        Destination directory.  If *None*, defaults to
        `<project-root>/data/processed`.
    fname_prefix : str
        Prefix for the output filename.
    include_index : bool
        Whether to write the dataframe index.
    compression : {"gzip","bz2","zip","xz"} | None
        Optional on-the-fly compression.

    Returns
    -------
    Path
        Full path of the file that was written.
    """
    # Input validation
    if not hasattr(df, "to_csv"):
        raise TypeError(f"Expected a pandas DataFrame, got {type(df)}")
    if compression and compression not in ALLOWED_COMPRESSIONS:
        raise ValueError(
            f"Invalid compression type: {compression}. "
            f"Allowed types are: {', '.join(ALLOWED_COMPRESSIONS)}"
        )

    # Prepare paths
    out_dir = Path(output_dir) if output_dir else _default_output_dir()
    out_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    ext = ".csv" if compression is None else f".csv.{compression}"
    out_path = out_dir / f"{fname_prefix}_{ts}{ext}"
    tmp_path = out_dir / f".{out_path.name}.tmp"

    # Disk space check
    _, _, free = shutil.disk_usage(out_dir)
    if df.memory_usage(deep=True).sum() * 1.1 > free:
        raise OSError(
            f"Not enough disk space to write the file. "
            f"Required: {df.memory_usage(deep=True).sum() * 1.1 / (1024**2):.2f} MB, "
            f"Available: {free / (1024**2):.2f} MB"
        )

    # Write with atomic
    start = time.time()
    try:
        _atomic_write(
            df,
            tmp_path,
            out_path,
            index=include_index,
            compression=compression,
        )
    except Exception as e:
        logger.exception(f"Failed to write file for [{out_path}] due to: {e}")

    # Final log
    duration = time.time() - start
    size_mb = out_path.stat().st_size / 1e6
    logger.info(
        f"Wrote {len(df)} records to {out_path.name} in {duration:.2f}s ({size_mb:.2f} MB)"
    )

    return out_path
