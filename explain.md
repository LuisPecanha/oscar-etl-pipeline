
# 📖 explain.md


## Project Overview

This project was based on a take-home assignment from YipitData, which required building a web scraping process and ETL pipeline to gather and clean data on Oscar-nominated movies from 1927 to 2014. The core task involved creating a toolkit or library of utility functions that could:

- Scrape data from a public API (`http://oscars.yipitdata.com/`)
- Extract additional details from secondary "Detail URLs"
- Clean and normalize messy fields — particularly the film budget
- Export a final CSV of structured, analysis-ready data

The target schema included: `film`, `year`, `wikipedia_url`, `oscar_winner`, `budget_original`, and `budget_usd`, with the expectation that any non-USD amounts be converted to USD and budget ranges be reduced to their lowest value.

As a bonus, I also opted to:
- Clean and normalize the `year` column
- Adjust budgets for inflation using historical CPI data
- Validate the final dataset using Pydantic
- Speed up data enrichment with concurrent requests
- Write unit tests for key transformation and extraction functions

Overall, the goal was to demonstrate my ability to design a clean, modular, and resilient data pipeline that can handle real-world inconsistencies and produce a reliable output for analysis.


---

## Extraction Strategy

I began by querying the base API to collect a list of Oscar-nominated films. Each entry had minimal metadata, so I enriched the dataset by fetching the budget, as required in task, for each film via its associated Detail URL.

To make this enrichment step performant, I used Python’s `concurrent.futures.ThreadPoolExecutor` to parallelize the HTTP requests. This significantly reduced processing time, especially when querying hundreds of URLs.

During enrichment, I encountered several `403 Forbidden` errors. Upon inspection, these errors were caused by malformed or double-encoded URLs. Rather than hardcoding fixes or skipping enrichment entirely, I handled them by:

- Attempting general sanitization (decoding and re-encoding URLs)
- Logging any failed URLs
- Skipping those that still failed after sanitization and tagging them with a error flag for traceability

This ensures that the pipeline remains robust and doesn’t break due to a few faulty records.

---

## Transformation Logic

The most inconsistent column was the budget. It appeared in multiple formats (e.g., "$6–7 million", "€10M", "$2 million [1]", etc.), currencies, and units. I wrote a custom function `parse_budget_value` to clean and normalize these into numeric USD values.

I opted to store two columns:
- `budget_original`: the raw budget string exactly as it appeared in the source
- `budget_usd`: a cleaned, parsed, and normalized value in USD

This design balances traceability and analytical utility. The raw string is preserved for auditability, while the parsed value supports filtering, sorting, and aggregation.

Through analysis, I found that currencies other than USD included **Euro (€)**, **British Pound (£)**, and **Italian Lira (₤)**. For these, I used exchange rates from the Frankfurter API, with a hard-coded fallback for the Lira based on historical rates, since it's no longer an active currency.

One special case I handled manually was _Avatar_, which had both an original budget and a re-release budget listed. I chose to sum these values into a single total for the `budget_usd` field, since both represented production investments tied to the same film. While this involved a small manual assumption, I considered it a reasonable exception given the clear context and analytical relevance. All other transformations remained strictly rule-based and derived directly from the source data.

---

## Inflation Adjustment

To make budgets from different eras comparable, I added a third column: `budget_updated`, which reflects inflation-adjusted values as of 2024.

I used historical U.S. CPI data from 1913 to 2024, initially retrieved from a public API and saved as a local JSON file (`cpi_us.json`) to avoid exposing keys. This approach keeps the pipeline self-contained and secure.

In a production-grade pipeline, this logic could be extended by:
- Automatically updating the CPI data on a schedule
- Storing the API key securely (e.g., using AWS Secrets Manager or GCP Secret Manager)

This inflation adjustment provides essential historical context, enabling a more accurate comparison of films spanning nearly a century.

---


## Data Validation Strategy

After transforming the dataset, I validated each record using a Pydantic model (`Movie`). This model enforced strict typing and logical constraints, including:

- `film`: non-empty string (with custom whitespace stripping logic)
- `year`: between 1878 and the current year
- `wikipedia_url`: valid HTTP URL
- `budget_usd` and `budget_updated`: non-negative integers, capped at 10 billion
- `budget_raw`: optional string, which allows for missing or unknown values

Validation was applied row-by-row. If a record failed any of the constraints, it was logged with details about the validation error, and excluded from the final result. Here's an example from the logs:



Rather than halting the pipeline on errors, I chose to log and skip invalid rows, preserving pipeline continuity. In a real-world scenario, this validation step could act as a critical gate, stopping execution and triggering alerts (Slack, email, etc.) if records fail.

This flexible approach let me flag issues while keeping the process resilient.

---


## Design Consideration: Layered Architecture

I considered implementing a layered architecture with `raw`, `trusted`, and `refined` zones. A common pattern in production-grade data pipelines. However, given the scope of this project, I opted for a simplified architecture.

The primary reason was that the dataset centered around a single domain entity: **movies**. There were no related dimensions or multiple interdependent models like clients, theaters, or production companies, which would typically justify a layered Medallion-style structure. Additionally, the pipeline was designed for one-time or occasional use rather than continuous reprocessing.

This simplified approach:
- Reduced architectural complexity
- Improved runtime performance
- Aligned better with the project’s scope and goals

If the domain had included more entities, or if the pipeline were intended for long-term maintenance or analytics use, I would have implemented a more formal layered architecture to improve modularity, auditing, and scalability.


---

## Tests

Although optional, I included tests to demonstrate that the codebase is modular and testable. I wrote unit tests for:

- `extract_awards_data`: using mocked API responses to validate extraction logic without hitting the network
- `parse_budget_value`: testing various edge cases (symbols, units, malformed values, etc.)

These tests act as a proof of concept for automated validation. In a real-world setting, this test suite could be expanded to:

- Cover transformation and validation steps
- Be integrated with a CI/CD workflow (e.g., via GitHub Actions)
- Enforce schema checks and data quality continuously

---

## Load Step

Finally, I saved the cleaned and validated data to a timestamped `.csv` file inside the `data/processed/` directory. This makes the results easy to inspect and allows for reproducibility.

The `load.py` module includes options for customizing the output location, filename, and compression. This could easily be extended to support uploads to S3, GCS, or a database in future iterations.

---

## Closing Thoughts

This project helped me demonstrate the core elements of a modern ETL pipeline:
- Modular extraction, transformation, and loading
- Concurrent processing for performance
- Input validation with graceful fallback
- Historical normalization via exchange rates and CPI inflation
- Test coverage and logging

It also allowed me to make realistic tradeoffs between simplicity and scalability, aligning with how data systems are built in the real world.