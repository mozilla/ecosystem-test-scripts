"""Entry point for the Google Sheet Uploader script."""

import argparse
import logging

from uploader import GoogleSheetUploader
from config import Config


def main(config_file: str = "config.ini"):
    """Run the Google Sheet Uploader.

    Args:
        config_file (str): Path to the configuration file. Defaults to 'config.ini'.
    """
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    logger.info("Starting Google Sheet Uploader")

    # Load configuration
    config = Config(config_file)
    logger.info("Configuration loaded successfully")

    # Create uploader instance
    uploader = GoogleSheetUploader(config)
    logger.info("Uploader instance created")

    # Process CSV files
    uploader.process_csv_files()
    logger.info("CSV files processed successfully")

    logger.info("Google Sheet Upload complete")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the Google Sheet Uploader")
    parser.add_argument("--config", help="Path to the config.ini file", default="config.ini")
    args = parser.parse_args()
    main(args.config)
