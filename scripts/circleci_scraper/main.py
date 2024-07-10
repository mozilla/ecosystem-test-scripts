# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""Entry point for CircleCI scraping"""

import argparse
import logging

from client import CircleCIClient, CircleCIClientError
from config import Config, InvalidConfigError
from scraper import CircleCIScraper, CircleCIScraperError

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def main(config_file: str = "config.ini") -> None:
    """Run the CircleCI scraper.

    Args:
        config_file (str): Path to the configuration file. Defaults to 'config.ini'.
    """
    try:
        config = Config(config_file)
        date_limit = config.circleci_scraper_config.date_limit
        logger.info(
            f"Scraping data from {date_limit.strftime('%Y-%m-%d %H:%M:%S')} to now."
            if date_limit
            else "Scraping all available data."
        )
        client = CircleCIClient(config.circleci_scraper_config)
        scraper = CircleCIScraper(config.main_config, client)
        scraper.export_test_metadata_and_artifacts(
            config.circleci_scraper_config.pipelines, config.circleci_scraper_config.date_limit
        )
        logger.info("Scraping complete")
    except InvalidConfigError as error:
        logger.error(f"Configuration error: {error}")
    except CircleCIClientError as error:
        logger.error(f"CircleCI Client error: {error}")
    except CircleCIScraperError as error:
        logger.error(f"CircleCI Scraper error: {error}")
    except Exception as error:
        logger.error(f"Unexpected error: {error}", exc_info=error)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the CircleCI Scraper")
    parser.add_argument("--config", help="Path to the config.ini file", default="config.ini")
    args = parser.parse_args()
    main(args.config)
