
# 📂 README.md

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
- `venv/`: Isolated environment

---

## How to Run

1. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the ETL pipeline:
   ```bash
   python src/main.py
   ```

4. Output will be saved under `data/processed/`.

---

## Key Features

- **Concurrent Enrichment**: Speeds up detail fetching using `ThreadPoolExecutor`
- **Budget Normalization**: Converts all currencies to USD and handles messy strings
- **Inflation Adjustment**: Uses CPI data to adjust historical budgets to 2024 dollars
- **Validation**: Pydantic models ensure schema correctness
- **Testing**: Pytest-based suite for extraction and transformation logic
- **Logging**: Structured logs for both ETL flow and data validation issues

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