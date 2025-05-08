
## Project Summary

This repository contains a complete ETL pipeline that extracts data on Oscar-nominated films (1927–2014), enriches it with additional details, cleans and normalizes key fields (like budgets), and exports the result to a clean CSV. The pipeline is modular, testable, and includes logging and validation.

---

## Architecture

The project follows a layered structure:

- `config/`: YAML configuration for logging and runtime settings  
- `data/`: Output storage (`raw/` for static resources, `processed/` for results)  
- `logs/`: Execution and validation logs  
- `src/`: Main logic organized by module (`etl/`, `models/`, `main.py`)  
- `tests/`: Unit tests for key components

---

## How to Run

1. Build the Docker image:
   ```bash
   docker build --build-arg HOST_UID=$(id -u) --build-arg HOST_GID=$(id -g) -t oscar-etl .
   ```

2. Run the container using your host UID/GID to avoid file permission issues:
   ```bash
   docker run --rm -v "$(pwd)/data/processed:/app/data/processed" -v "$(pwd)/logs:/app/logs" oscar-etl
   ```

3. The cleaned CSV will be saved to `data/processed/` on your host machine.

---

## Key Features

- **Concurrent Enrichment**: Speeds up detail fetching using `ThreadPoolExecutor`
- **Budget Normalization**: Converts all currencies to USD and handles messy strings
- **Inflation Adjustment**: Uses CPI data to adjust historical budgets to 2024 dollars
- **Validation**: Pydantic models ensure schema correctness
- **Testing**: Pytest-based suite for extraction and transformation logic
- **Logging**: Structured logs for both ETL flow and data validation issues
- **Dockerized Execution**: Fully reproducible and isolated environment for running the pipeline

---

## Testing

To run the tests:

```bash
pytest
```

Covers:
- API extraction (with mocked responses)
- Budget parsing and transformation

---

## Configuration

- `config/settings.yaml`: API URLs and static paths  
- `config/logging.yaml`: Log format and level  
- `data/raw/cpi_us.json`: Local CPI values to avoid API exposure  