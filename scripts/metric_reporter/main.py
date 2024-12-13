# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""Main module for running the Metric Reporter."""

import argparse
import logging

from google.cloud import bigquery
from google.oauth2 import service_account

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


def main(
    config_file: str = "config.ini",
    output_csv: bool | None = None,
    update_bigquery: bool | None = None,
) -> None:
    """Run the Metric Reporter.

    Args:
        config_file (str): Path to the configuration file.
        output_csv (bool | None): Whether to output CSV files. Overrides config file if provided.
        update_bigquery (bool | None): Whether to update BigQuery tables. Overrides config file if provided.
    """
    try:
        logger.info(f"Starting Metric Reporter with configuration file: {config_file}")
        config = Config(config_file)
        gcp_project_id: str = config.metric_reporter_config.gcp_project_id
        bigquery_dataset_name: str = config.metric_reporter_config.bigquery_dataset_name
        bigquery_service_account_file: str = (
            config.metric_reporter_config.bigquery_service_account_file
        )
        output_csv = (
            output_csv if output_csv is not None else config.metric_reporter_config.output_csv
        )
        update_bigquery = (
            update_bigquery
            if update_bigquery is not None
            else config.metric_reporter_config.update_bigquery
        )

        # Create Parsers
        circleci_parser = CircleCIJsonParser()
        coverage_json_parser = CoverageJsonParser()
        junit_xml_parser = JUnitXmlParser()

        # Create BigQuery client
        credentials = service_account.Credentials.from_service_account_file(
            bigquery_service_account_file
        )  # type: ignore
        bigquery_client = bigquery.Client(credentials=credentials, project=gcp_project_id)

        for args in config.metric_reporter_args:
            logger.info(f"Reporting for {args.repository} {args.workflow} {args.test_suite}")

            # Parse files
            metadata_list: list[CircleCIJobTestMetadata] | None = None
            if args.metadata_path.is_dir():
                metadata_list = circleci_parser.parse(args.metadata_path)
            junit_artifact_list: list[JUnitXmlJobTestSuites] | None = None
            if args.junit_artifact_path.is_dir():
                junit_artifact_list = junit_xml_parser.parse(args.junit_artifact_path)
            coverage_artifact_list: list[LlvmCovReport | PytestReport] | None = None
            if args.coverage_artifact_path.is_dir():
                coverage_artifact_list = coverage_json_parser.parse(args.coverage_artifact_path)

            # Create reporters
            suite_reporter = SuiteReporter(
                args.repository, args.workflow, args.test_suite, metadata_list, junit_artifact_list
            )
            averages_reporter = AveragesReporter(
                args.repository, args.workflow, args.test_suite, suite_reporter.results
            )
            coverage_reporter = CoverageReporter(
                args.repository, args.workflow, args.test_suite, coverage_artifact_list
            )

            if not output_csv and not update_bigquery:
                logger.warning(
                    "The metric reporter will not perform any action. Use the --output-csv or"
                    " --update-bigquery flags."
                )
                return

            # Output CSV files if opted-in
            if output_csv:
                averages_reporter.output_csv(args.averages_csv_report_path)
                coverage_reporter.output_csv(args.coverage_csv_report_path)
                suite_reporter.output_csv(args.results_csv_report_path)

            # Update BigQuery dataset tables if opted-in
            if update_bigquery:
                averages_reporter.update_table(
                    bigquery_client, gcp_project_id, bigquery_dataset_name
                )
                coverage_reporter.update_table(
                    bigquery_client, gcp_project_id, bigquery_dataset_name
                )
                suite_reporter.update_table(bigquery_client, gcp_project_id, bigquery_dataset_name)

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
    parser.add_argument("--output-csv", help="Output CSV files", type=bool, default=None)
    parser.add_argument(
        "--update-bigquery", help="Update BigQuery tables", type=bool, default=None
    )
    parser_args = parser.parse_args()
    main(
        parser_args.config,
        output_csv=parser_args.output_csv,
        update_bigquery=parser_args.update_bigquery,
    )
