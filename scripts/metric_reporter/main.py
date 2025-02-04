# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""Main module for running the Metric Reporter."""

import argparse
import logging

from google.cloud import bigquery
from google.oauth2 import service_account

from scripts.metric_reporter.config import Config, InvalidConfigError, MetricReporterArgs
from scripts.metric_reporter.parser.base_parser import ParserError
from scripts.metric_reporter.parser.coverage_json_parser import (
    CoverageJsonGroup,
    CoverageJsonParser,
)
from scripts.metric_reporter.parser.junit_xml_parser import JUnitXmlParser, JUnitXmlGroup
from scripts.metric_reporter.reporter.averages_reporter import AveragesReporter
from scripts.metric_reporter.reporter.base_reporter import ReporterError
from scripts.metric_reporter.reporter.coverage_reporter import CoverageReporter
from scripts.metric_reporter.reporter.suite_reporter import SuiteReporter

# Configure logging
logging.basicConfig(level=logging.WARNING, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def main(
    config_file: str = "config.ini",
    update_bigquery: bool | None = None,
) -> None:
    """Run the Metric Reporter.

    Args:
        config_file (str): Path to the configuration file.
        update_bigquery (bool | None): Whether to update BigQuery tables. Overrides config file if provided.
    """
    try:
        logger.info(f"Starting Metric Reporter with configuration file: {config_file}")
        config = Config(config_file)
        metric_reporter_args: list[MetricReporterArgs] = config.metric_reporter_args
        gcp_project_id: str = config.metric_reporter_config.gcp_project_id
        bigquery_dataset_name: str = config.metric_reporter_config.bigquery_dataset_name
        bigquery_service_account_file: str = (
            config.metric_reporter_config.bigquery_service_account_file
        )
        if update_bigquery is None:
            update_bigquery = config.metric_reporter_config.update_bigquery
        if not update_bigquery:
            logger.warning(
                "The metric reporter will not perform any action. "
                "Use the --update-bigquery flag."
            )
            return

        # Create BigQuery client
        credentials = service_account.Credentials.from_service_account_file(
            bigquery_service_account_file
        )  # type: ignore
        bigquery_client = bigquery.Client(credentials=credentials, project=gcp_project_id)

        # Report
        report_coverage(
            metric_reporter_args, bigquery_client, gcp_project_id, bigquery_dataset_name
        )
        report_suite_results_and_averages(
            metric_reporter_args, bigquery_client, gcp_project_id, bigquery_dataset_name
        )
    except InvalidConfigError as error:
        logger.error(f"Configuration error: {error}")
    except ParserError as error:
        logger.error(f"Parsing error: {error}")
    except ReporterError as error:
        logger.error(f"Test Suite Reporter error: {error}")
    except Exception as error:
        logger.error(f"Unexpected error: {error}", exc_info=error)


def report_coverage(
    metric_reporter_args: list[MetricReporterArgs],
    bigquery_client,
    gcp_project_id: str,
    bigquery_dataset_name: str,
) -> None:
    """Report results from Coverage JSON files to a BigQuery dataset table.

    Args:
        metric_reporter_args (list[MetricReporterArgs]): Configuration arguments.
        bigquery_client: BigQuery client
        gcp_project_id (str): The GCP project ID.
        bigquery_dataset_name (str): The name of the BigQuery dataset.
    """
    coverage_json_parser = CoverageJsonParser()
    coverage_artifact_groups: list[CoverageJsonGroup] = [
        group
        for args in metric_reporter_args
        for group in coverage_json_parser.parse(args.coverage_artifact_paths)
    ]
    for group in coverage_artifact_groups:
        logger.info(f"Report coverage for {group.repository} {group.workflow} {group.test_suite}")
        coverage_reporter = CoverageReporter(
            group.repository, group.workflow, group.test_suite, group.coverage_jsons
        )
        coverage_reporter.update_table(bigquery_client, gcp_project_id, bigquery_dataset_name)


def report_suite_results_and_averages(
    metric_reporter_args: list[MetricReporterArgs],
    bigquery_client,
    gcp_project_id: str,
    bigquery_dataset_name: str,
) -> None:
    """Report results from JUnit XML files to BigQuery dataset tables.

    Args:
        metric_reporter_args (list[MetricReporterArgs]): Configuration arguments.
        bigquery_client: BigQuery client
        gcp_project_id (str): The GCP project ID.
        bigquery_dataset_name (str): The name of the BigQuery dataset.
    """
    junit_xml_parser = JUnitXmlParser()
    junit_artifact_groups: list[JUnitXmlGroup] = [
        group
        for args in metric_reporter_args
        for group in junit_xml_parser.parse(args.junit_artifact_paths)
    ]
    for group in junit_artifact_groups:
        logger.info(
            f"Reporting results for {group.repository} {group.workflow} {group.test_suite}"
        )
        suite_reporter = SuiteReporter(
            group.repository, group.workflow, group.test_suite, group.junit_xmls
        )
        averages_reporter = AveragesReporter(
            group.repository, group.workflow, group.test_suite, suite_reporter.results
        )
        suite_reporter.update_table(bigquery_client, gcp_project_id, bigquery_dataset_name)
        averages_reporter.update_table(bigquery_client, gcp_project_id, bigquery_dataset_name)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the Metric Reporter")
    parser.add_argument("--config", help="Path to the config.ini file", default="config.ini")
    parser.add_argument(
        "--update-bigquery", help="Update BigQuery tables", type=bool, default=None
    )
    parser_args = parser.parse_args()
    main(
        parser_args.config,
        update_bigquery=parser_args.update_bigquery,
    )
