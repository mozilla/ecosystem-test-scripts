# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""Main module for running the Metric Reporter."""

import argparse
import logging

from scripts.metric_reporter.config import Config, InvalidConfigError
from scripts.metric_reporter.parser.base_parser import ParserError
from scripts.metric_reporter.parser.circleci_json_parser import (
    CircleCIJsonParser,
    CircleCIJobTestMetadata,
)
from scripts.metric_reporter.parser.coverage_json_parser import (
    CoverageJsonParser,
    LlvmCovReport,
    PytestReport,
)
from scripts.metric_reporter.parser.junit_xml_parser import JUnitXmlJobTestSuites, JUnitXmlParser
from scripts.metric_reporter.reporter.averages_reporter import AveragesReporter
from scripts.metric_reporter.reporter.base_reporter import ReporterError
from scripts.metric_reporter.reporter.coverage_reporter import CoverageReporter
from scripts.metric_reporter.reporter.suite_reporter import SuiteReporter

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
        circleci_parser = CircleCIJsonParser()
        coverage_json_parser = CoverageJsonParser()
        junit_xml_parser = JUnitXmlParser()
        for args in config.metric_reporter_args:
            logger.info(f"Reporting for {args.repository} {args.workflow} {args.test_suite}")
            metadata_list: list[CircleCIJobTestMetadata] | None = None
            if args.metadata_path.is_dir():
                metadata_list = circleci_parser.parse(args.metadata_path)

            junit_artifact_list: list[JUnitXmlJobTestSuites] | None = None
            if args.junit_artifact_path.is_dir():
                junit_artifact_list = junit_xml_parser.parse(args.junit_artifact_path)

            coverage_artifact_list: list[LlvmCovReport | PytestReport] | None = None
            if args.coverage_artifact_path.is_dir():
                coverage_artifact_list = coverage_json_parser.parse(args.coverage_artifact_path)

            suite_reporter = SuiteReporter(
                args.repository, args.workflow, args.test_suite, metadata_list, junit_artifact_list
            )
            suite_reporter.output_csv(args.results_csv_report_path)

            averages_reporter = AveragesReporter(
                args.repository, args.workflow, args.test_suite, suite_reporter.results
            )
            averages_reporter.output_csv(args.averages_csv_report_path)

            coverage_reporter = CoverageReporter(
                args.repository, args.workflow, args.test_suite, coverage_artifact_list
            )
            coverage_reporter.output_csv(args.coverage_csv_report_path)
        logger.info("Reporting complete")
    except InvalidConfigError as error:
        logger.error(f"Configuration error: {error}")
    except ParserError as error:
        logger.error(f"Parsing error: {error}")
    except ReporterError as error:
        logger.error(f"Test Suite Reporter error: {error}")
    except Exception as error:
        logger.error(f"Unexpected error: {error}", exc_info=error)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the Metric Reporter")
    parser.add_argument("--config", help="Path to the config.ini file", default="config.ini")
    parser_args = parser.parse_args()
    main(parser_args.config)
