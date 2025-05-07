from logging_config import setup_logging
from etl.extract import extract_awards_data, enrich_with_film_details
import logging


def execute():
    """
    Main function to execute the ETL process.
    """

    setup_logging()
    logger = logging.getLogger("etl.main")
    logger.info("Starting ETL process...")

    # Extract
    df = extract_awards_data()

    # Enrich film data with details
    df_full = enrich_with_film_details(df)

    #print(df_full)

    # Load
    # Here you would typically load the data into a database or file
    df_full.to_csv("../data/enriched_oscar_data.csv", index=False)

if __name__ == "__main__":
    execute()
