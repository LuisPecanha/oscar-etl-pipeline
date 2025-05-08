import logging

from logging_config import setup_logging
from etl.extract import extract_awards_data, enrich_with_film_details
from etl.transform import clean_budget_column, clean_year_column
from etl.validate import validate_movies
from etl.load import to_csv

def execute():
    """
    Main function to execute the ETL pipeline.
    """

    setup_logging()
    logger = logging.getLogger("etl.main")
    logger.info("Starting ETL pipeline...")

    # Extract
    logger.info("Extracting data...")
    df = extract_awards_data()

    # Enrich film data with details
    df_full = enrich_with_film_details(df)

    # Process and clean data
    logger.info("Processing data...")
    df_full = clean_budget_column(df_full)
    df_full = clean_year_column(df_full)

    logger.info("Validating data...")
    validated_df = validate_movies(df_full)

    # Load
    logger.info("Loading data...")
    output_path = to_csv(validated_df)

    logger.info(f"Pipeline completed. Data saved to {output_path}")
    

if __name__ == "__main__":
    execute()
