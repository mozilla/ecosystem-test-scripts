# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""Main module for running the Metric Reporter."""

import argparse
import logging

from scripts.metric_reporter.averages_reporter import AveragesReporter
from scripts.metric_reporter.base_reporter import ReporterError
from scripts.metric_reporter.circleci_json_parser import (
    CircleCIJsonParserError,
    CircleCIJsonParser,
    CircleCIJobTestMetadata,
)
from scripts.metric_reporter.config import Config, InvalidConfigError
from scripts.metric_reporter.junit_xml_parser import (
    JUnitXmlJobTestSuites,
    JUnitXmlParser,
    JUnitXmlParserError,
)
from scripts.metric_reporter.suite_reporter import SuiteReporter

# Configure logging
logging.basicConfig(level=logging.WARNING, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def main(config_file: str = "config.ini") -> None:
    """Run the Metric Reporter.

    Args:
        config_file (str): Path to the configuration file.
                           Defaults to 'ecosystem-test-scripts/config.ini'.
    """
    try:
        logger.info(f"Starting Metric Reporter with configuration file: {config_file}")
        config = Config(config_file)
        for args in config.metric_reporter_args:
            logger.info(f"Reporting for {args.repository} {args.workflow} {args.test_suite}")
            metadata_list: list[CircleCIJobTestMetadata] | None = None
            if args.metadata_path.is_dir():
                circleci_parser = CircleCIJsonParser()
                metadata_list = circleci_parser.parse(args.metadata_path)

            junit_artifact_list: list[JUnitXmlJobTestSuites] | None = None
            if args.junit_artifact_path.is_dir():
                junit_xml_parser = JUnitXmlParser()
                junit_artifact_list = junit_xml_parser.parse(args.junit_artifact_path)

            suite_reporter = SuiteReporter(
                args.repository, args.workflow, args.test_suite, metadata_list, junit_artifact_list
            )
            suite_reporter.output_csv(args.results_csv_report_path)

            averages_reporter = AveragesReporter(
                args.repository, args.workflow, args.test_suite, suite_reporter.results
            )
            averages_reporter.output_csv(args.averages_csv_report_path)
        logger.info("Reporting complete")
    except InvalidConfigError as error:
        logger.error(f"Configuration error: {error}")
    except CircleCIJsonParserError as error:
        logger.error(f"CircleCI JSON Parsing error: {error}")
    except JUnitXmlParserError as error:
        logger.error(f"JUnit XML Parsing error: {error}")
    except ReporterError as error:
        logger.error(f"Test Suite Reporter error: {error}")
    except Exception as error:
        logger.error(f"Unexpected error: {error}", exc_info=error)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the Metric Reporter")
    parser.add_argument("--config", help="Path to the config.ini file", default="config.ini")
    parser_args = parser.parse_args()
    main(parser_args.config)
