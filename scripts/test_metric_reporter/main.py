# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""Main module for running the Test Metric Reporter."""

import argparse
import logging

from scripts.test_metric_reporter.circleci_json_parser import CircleCIJsonParserError
from scripts.test_metric_reporter.config import Config, InvalidConfigError
from scripts.test_metric_reporter.suite_reporter import SuiteReporter, SuiteReporterError

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def main(config_file: str = "config.ini") -> None:
    """Run the Test Metric Reporter.

    Args:
        config_file (str): Path to the configuration file. Defaults to 'ecosystem-test-scripts/config.ini'.
    """
    try:
        logger.info(f"Starting Test Metric Reporter with configuration file: {config_file}")
        config = Config(config_file)
        for test_metric_reporter_args in config.test_metric_reporter_args:
            reporter = SuiteReporter(test_metric_reporter_args.test_metadata_directory_path)
            reporter.output_results_csv(test_metric_reporter_args.csv_report_file_path)
        logger.info("Reporting complete")
    except InvalidConfigError as error:
        logger.error(f"Configuration error: {error}")
    except CircleCIJsonParserError as error:
        logger.error(f"CircleCI JSON Parsing error: {error}")
    except SuiteReporterError as error:
        logger.error(f"Test Suite Reporter error: {error}")
    except Exception as error:
        logger.error(f"Unexpected error: {error}", exc_info=error)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the Test Metric Reporter")
    parser.add_argument("--config", help="Path to the config.ini file", default="config.ini")
    args = parser.parse_args()
    main(args.config)
