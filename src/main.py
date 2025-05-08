import logging
from time import perf_counter
from logging_config import setup_logging
from etl import extract, transform, validate, load

def execute():
    """
    Main function to execute the ETL pipeline.
    """

    setup_logging()
    logger = logging.getLogger("etl.main")
    logger.info("Starting ETL pipeline...")
    t0 = perf_counter()

    # 1 - Extract data
    logger.info("Extracting data...")
    df_raw = extract()

    # 2 - Process and clean data
    logger.info("Processing data...")
    df_clean = transform(df_raw)

    # 3 - Validate data
    logger.info("Validating data...")
    df_validated = validate(df_clean)

    # 4 - Load data
    logger.info("Loading data...")
    output_path = load(df_validated)

    logger.info(f"Pipeline completed. Data saved to {output_path}")
    logger.info(f"ETL pipeline completed in {perf_counter() - t0:.2f} seconds.")
    

if __name__ == "__main__":
    execute()
