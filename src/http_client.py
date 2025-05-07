import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/112.0.0.0 Safari/537.36"
    )
}


def make_session(
    total_retries: int = 5,
    backoff_factor: float = 0.5,
    status_forcelist: tuple = (429, 500, 502, 503, 504),
    pool_connections: int = 20,
    pool_maxsize: int = 20,
    pool_block: bool = True,
) -> requests.Session:
    """
    Create a requests session with retry logic and an increased connection pool.

    Args:
        total_retries (int): Total number of retries for 5xx and 429 statuses.
        backoff_factor (float): Delay factor between retries.
        status_forcelist (tuple): HTTP status codes to retry on.
        pool_connections (int): Number of connection pools to maintain.
        pool_maxsize (int): Maximum number of connections in each pool.
        pool_block (bool): Block when pool is exhausted.

    Returns:
        requests.Session: A requests session with retry and pooling configured.
    """
    session = requests.Session()
    retry = Retry(
        total=total_retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
        allowed_methods=frozenset(["GET", "POST", "PUT", "DELETE", "HEAD", "OPTIONS"]),
        raise_on_status=False,
    )
    adapter = HTTPAdapter(
        max_retries=retry,
        pool_connections=pool_connections,
        pool_maxsize=pool_maxsize,
        pool_block=pool_block,
    )
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    session.headers.update(HEADERS)
    return session


# initialize a module‐level session with an enlarged pool
SESSION = make_session()
