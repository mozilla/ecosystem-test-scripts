# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""Main module for running the Metric Reporter."""

import argparse
import logging

from google.cloud import bigquery, storage
from google.oauth2.service_account import Credentials

from scripts.metric_reporter.config import Config, InvalidConfigError
from scripts.metric_reporter.gcs_client import GCSClient, GCSArtifacts, GCSClientError
from scripts.metric_reporter.parser.base_parser import ParserError
from scripts.metric_reporter.parser.coverage_json_parser import (
    CoverageJsonGroup,
    CoverageJsonParser,
)
from scripts.metric_reporter.parser.junit_xml_parser import JUnitXmlParser, JUnitXmlGroup
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
        update_bigquery (bool | None): Whether to update BigQuery tables. Overrides config file if
                                       provided.
    """
    try:
        logger.info(f"Starting Metric Reporter with configuration file: {config_file}")
        config = Config(config_file)
        gcp_project_id: str = config.common_config.gcp_project_id
        test_result_bucket: str = config.common_config.test_result_bucket
        coverage_artifact_dir: str = config.common_config.coverage_artifact_dir
        junit_artifact_dir: str = config.common_config.junit_artifact_dir
        bigquery_dataset_name: str = config.metric_reporter_config.bigquery_dataset_name
        service_account_file: str = config.metric_reporter_config.service_account_file
        if update_bigquery is None:
            update_bigquery = config.metric_reporter_config.update_bigquery
        if not update_bigquery:
            logger.warning(
                "The metric reporter will not perform any action. "
                "Use the --update-bigquery flag."
            )
            return

        # Create GCS and BigQuery clients
        credentials = Credentials.from_service_account_file(service_account_file)  # type: ignore
        storage_client = storage.Client(project=gcp_project_id, credentials=credentials)
        bigquery_client = bigquery.Client(project=gcp_project_id, credentials=credentials)

        # Report
        gcs_client = GCSClient(
            storage_client, test_result_bucket, coverage_artifact_dir, junit_artifact_dir
        )
        gcs_artifacts: list[GCSArtifacts] = gcs_client.get_artifacts()
        report_coverage(
            gcs_client, gcs_artifacts, bigquery_client, gcp_project_id, bigquery_dataset_name
        )
        report_suite_results(
            gcs_client, gcs_artifacts, bigquery_client, gcp_project_id, bigquery_dataset_name
        )
    except InvalidConfigError as error:
        logger.error(f"Configuration error: {error}")
    except GCSClientError as error:
        logger.error(f"GCS client error: {error}")
    except ParserError as error:
        logger.error(f"Parsing error: {error}")
    except ReporterError as error:
        logger.error(f"Test Suite Reporter error: {error}")
    except Exception as error:
        logger.error(f"Unexpected error: {error}", exc_info=error)


def report_coverage(
    gcs_client: GCSClient,
    gcs_artifacts: list[GCSArtifacts],
    bigquery_client,
    gcp_project_id: str,
    bigquery_dataset_name: str,
) -> None:
    """Report results from Coverage JSON files to a BigQuery dataset table.

    Args:
        gcs_client (GCSClient): Storage client
        gcs_artifacts (list[GCSArtifacts]): Lists of artifact files grouped by repository
        bigquery_client: BigQuery client
        gcp_project_id (str): The GCP project ID.
        bigquery_dataset_name (str): The name of the BigQuery dataset.
    """
    coverage_json_parser = CoverageJsonParser(gcs_client)
    coverage_artifact_groups: list[CoverageJsonGroup] = [
        group
        for artifacts in gcs_artifacts
        for group in coverage_json_parser.parse(artifacts.coverage_artifact_files)
    ]
    for group in coverage_artifact_groups:
        logger.info(f"Report coverage for {group.repository} {group.workflow} {group.test_suite}")
        coverage_reporter = CoverageReporter(
            group.repository, group.workflow, group.test_suite, group.coverage_jsons
        )
        coverage_reporter.update_table(bigquery_client, gcp_project_id, bigquery_dataset_name)


def report_suite_results(
    gcs_client: GCSClient,
    gcs_artifacts: list[GCSArtifacts],
    bigquery_client,
    gcp_project_id: str,
    bigquery_dataset_name: str,
) -> None:
    """Report results from JUnit XML files to BigQuery dataset tables.

    Args:
        gcs_client (GCSClient): Storage client
        gcs_artifacts (list[GCSArtifacts]): Lists of artifact files grouped by repository
        bigquery_client: BigQuery client
        gcp_project_id (str): The GCP project ID.
        bigquery_dataset_name (str): The name of the BigQuery dataset.
    """
    junit_xml_parser = JUnitXmlParser(gcs_client)
    junit_artifact_groups: list[JUnitXmlGroup] = [
        group
        for artifacts in gcs_artifacts
        for group in junit_xml_parser.parse(artifacts.junit_artifact_files)
    ]
    for group in junit_artifact_groups:
        logger.info(f"Report results for {group.repository} {group.workflow} {group.test_suite}")
        suite_reporter = SuiteReporter(
            group.repository, group.workflow, group.test_suite, group.junit_xmls
        )
        suite_reporter.update_table(bigquery_client, gcp_project_id, bigquery_dataset_name)


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
