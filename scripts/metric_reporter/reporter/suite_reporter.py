# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""Module for reporting test suite results from CircleCI metadata."""

from datetime import datetime
from enum import Enum
from typing import Any, Sequence

from google.api_core.exceptions import GoogleAPIError
from google.cloud.bigquery import ArrayQueryParameter, Client, QueryJobConfig, ScalarQueryParameter
from pydantic import BaseModel

from scripts.metric_reporter.constants import DATETIME_FORMAT
from scripts.metric_reporter.parser.junit_xml_parser import (
    JestJUnitXmlTestSuites,
    JUnitXmlJobTestSuites,
    MochaJUnitXmlTestSuites,
    NextestJUnitXmlTestSuites,
    PlaywrightJUnitXmlTestSuites,
    PytestJUnitXmlTestSuites,
    TapJUnitXmlTestSuites,
)
from scripts.metric_reporter.reporter.base_reporter import (
    BaseReporter,
    ReporterError,
    ReporterResultBase,
)

SUCCESS_RESULTS = {"success", "system-out"}
FAILURE_RESULT = "failure"
SKIPPED_RESULT = "skipped"
CANCELED_JOB_STATUS = "canceled"
RUNNING_JOB_STATUS = "running"


class Status(Enum):
    """Overall status of the test suite."""

    SUCCESS = "success"
    FAILED = "failed"


class SuiteReporterResult(ReporterResultBase):
    """Represents the results of a test suite run."""

    repository: str
    workflow: str
    test_suite: str
    timestamp: str
    date: str
    job: int

    @property
    def status(self) -> Status:
        """Test Suite status"""
        if self.failure > 0:
            return Status.FAILED
        return Status.SUCCESS

    # The summation of all test run times in seconds. Parallelization is not taken into
    # consideration.
    # Not supported by TAP
    run_time: float = 0

    # Equal to the longest run_time in seconds when tests are run in parallel. We know tests are run
    # in parallel if we have multiple reports for a repository/workflow/test_suite.
    # Not supported by TAP
    execution_time: float | None = None

    success: int = 0
    failure: int = 0
    skipped: int = 0

    # An annotation available in Playwright only. Subset of 'skipped'.
    fixme: int = 0

    # The number of tests that were the result of a re-execution. It is possible that the same test
    # is re-executed more than once. Playwright only.
    retry: int = 0

    @property
    def total(self) -> int:
        """Calculate the total number of tests."""
        return self.success + self.failure + self.skipped

    @property
    def success_rate(self) -> float | None:
        """Calculate the success rate of the test suite."""
        return self._calculate_rate(self.success, self.total)

    @property
    def failure_rate(self) -> float | None:
        """Calculate the failure rate of the test suite."""
        return self._calculate_rate(self.failure, self.total)

    @property
    def skipped_rate(self) -> float | None:
        """Calculate the skipped rate of the test suite."""
        return self._calculate_rate(self.skipped, self.total)

    @property
    def fixme_rate(self) -> float | None:
        """Calculate the fixme rate of the test suite."""
        return self._calculate_rate(self.fixme, self.total)

    @staticmethod
    def _calculate_rate(value: int, total: int) -> float | None:
        """Calculate the percentage rate of a given value over the total.

        Args:
            value (int): The numerator for the rate calculation.
            total (int): The denominator for the rate calculation.

        Returns:
            float | None: The calculated rate as a percentage, or None if the total is 0.
        """
        return round((value / total) * 100, 2) if total > 0 else None

    def dict_with_fieldnames(self) -> dict[str, Any]:
        """Convert the test suite result to a dictionary with field names.

        Returns:
            dict[str, Any]: Dictionary representation of the test suite result.
        """
        return {
            "Repository": self.repository,
            "Workflow": self.workflow,
            "Test Suite": self.test_suite,
            "Date": self.date,
            "Timestamp": self.timestamp,
            "Job Number": self.job,
            "Status": self.status.value,
            "Execution Time": self.execution_time,
            "Run Time": self.run_time,
            "Success": self.success,
            "Failure": self.failure,
            "Skipped": self.skipped,
            "Fixme": self.fixme,
            "Retry Count": self.retry,
            "Total": self.total,
            "Success Rate": self.success_rate,
            "Failure Rate": self.failure_rate,
            "Skipped Rate": self.skipped_rate,
            "Fixme Rate": self.fixme_rate,
        }


class SuiteMetrics(BaseModel):
    """Represents the results of a test suite."""

    time: float | None = None
    tests: int = 0
    failure: int = 0
    skipped: int = 0
    fixme: int = 0
    retry: int = 0

    @property
    def success(self) -> int:
        """Calculate the number of tests that succeeded."""
        return self.tests - self.failure - self.skipped


class SuiteReporter(BaseReporter):
    """Handles the reporting of test suite results from CircleCI metadata and JUnit XML Reports."""

    def __init__(
        self,
        repository: str,
        workflow: str,
        test_suite: str,
        junit_artifact_list: list[JUnitXmlJobTestSuites] | None,
    ) -> None:
        """Initialize the reporter with the directory containing test result data.

        Args:
            repository (str): The repository associated to the test suite.
            workflow (str): The workflow associated to the test suite.
            test_suite (str): The test suite name.
            junit_artifact_list (list[JUnitXmlJobTestSuites] | None): The test results from JUnit
                                                                      XML artifacts.
        """
        super().__init__()
        self.repository = repository
        self.workflow = workflow
        self.test_suite = test_suite
        self.results: Sequence[SuiteReporterResult] = self._parse_results(junit_artifact_list)

    def update_table(self, client: Client, project_id: str, dataset_name: str) -> None:
        """Update the BigQuery table with new results.

        Args:
            client (Client): The BigQuery client to interact with BigQuery.
            project_id (str): The BigQuery project ID.
            dataset_name (str): The BigQuery dataset name.
        """
        table_id = (
            f"{project_id}.{dataset_name}.{self._normalize_name(self.repository)}_suite_results"
        )

        if not self.results:
            self.logger.warning(
                f"There are no results for {self.repository}/{self.workflow}/{self.test_suite} to "
                f"add to {table_id}."
            )
            return

        last_update: datetime | None = self._get_last_update(client, table_id)

        # If no 'last_update' insert all results, else insert results that occur after the last
        # update timestamp
        new_results: Sequence[SuiteReporterResult] = (
            self.results
            if not last_update
            else [
                r
                for r in self.results
                if r.timestamp and datetime.strptime(r.timestamp, DATETIME_FORMAT) > last_update
            ]
        )
        if not new_results:
            self.logger.warning(
                f"There are no new results for {self.repository}/{self.workflow}/{self.test_suite} "
                f"to add to {table_id}."
            )
            return

        self._insert_rows(client, table_id, new_results)

    def _check_rows_exist(
        self, client: Client, table_id: str, results: Sequence[SuiteReporterResult]
    ) -> bool:
        query = f"""
            SELECT 1
            FROM `{table_id}`
            WHERE `Job Number` IN UNNEST(@job_numbers)
            LIMIT 1
        """  # nosec
        jobs: list[int] = [result.job for result in results]
        query_parameters = [ArrayQueryParameter("job_numbers", "INT64", jobs)]
        job_config = QueryJobConfig(query_parameters=query_parameters)
        try:
            query_job = client.query(query, job_config=job_config)
            return any(query_job.result())
        except (GoogleAPIError, TypeError, ValueError) as error:
            error_mapping: dict[type, str] = {
                GoogleAPIError: f"Error executing query: {query}",
                TypeError: f"The query, {query}, has an invalid format or type",
                ValueError: f"The table name {table_id} is invalid",
            }
            error_msg: str = next(m for t, m in error_mapping.items() if isinstance(error, t))
            self.logger.error(error_msg, exc_info=error)
            raise ReporterError(error_msg) from error

    def _get_last_update(self, client: Client, table_id: str) -> datetime | None:
        query = f"""
            SELECT FORMAT_TIMESTAMP('{DATETIME_FORMAT}', MAX(`Timestamp`)) as last_update
            FROM `{table_id}`
            WHERE Repository = @repository AND Workflow = @workflow AND `Test Suite` = @test_suite
        """  # nosec
        query_parameters = [
            ScalarQueryParameter("repository", "STRING", self.repository),
            ScalarQueryParameter("workflow", "STRING", self.workflow),
            ScalarQueryParameter("test_suite", "STRING", self.test_suite),
        ]
        job_config = QueryJobConfig(query_parameters=query_parameters)
        try:
            query_job = client.query(query, job_config=job_config)
            result = query_job.result()
            for row in result:
                last_update: str | None = row["last_update"]
                return datetime.strptime(last_update, DATETIME_FORMAT) if last_update else None
        except (GoogleAPIError, TypeError, ValueError) as error:
            error_mapping: dict[type, str] = {
                GoogleAPIError: f"Error executing query: {query}",
                TypeError: f"The query, {query}, has an invalid format or type",
                ValueError: f"The table name {table_id} is invalid",
            }
            error_msg: str = next(m for t, m in error_mapping.items() if isinstance(error, t))
            self.logger.error(error_msg, exc_info=error)
            raise ReporterError(error_msg) from error
        return None

    def _insert_rows(
        self, client: Client, table_id: str, results: Sequence[SuiteReporterResult]
    ) -> None:
        results_exist: bool = self._check_rows_exist(client, table_id, results)
        if results_exist:
            self.logger.warning(
                f"Detected one or more results from "
                f"{self.repository}/{self.workflow}/{self.test_suite} already exist in table "
                f"{table_id}. Aborting insert."
            )
            return

        try:
            json_rows: list[dict[str, Any]] = [
                results.dict_with_fieldnames() for results in results
            ]
            errors = client.insert_rows_json(table_id, json_rows)
            if errors:
                client_error_msg: str = (
                    f"Failed to insert rows from "
                    f"{self.repository}/{self.workflow}/{self.test_suite} into {table_id}: {errors}"
                )
                self.logger.error(client_error_msg)
                raise ReporterError(client_error_msg)
            self.logger.info(
                f"Inserted {len(results)} results from "
                f"{self.repository}/{self.workflow}/{self.test_suite} into {table_id}."
            )
        except (TypeError, ValueError) as error:
            error_mapping: dict[type, str] = {
                TypeError: f"data is an improper format for insertion in {table_id}",
                ValueError: f"The table name {table_id} is invalid",
            }
            error_msg: str = next(m for t, m in error_mapping.items() if isinstance(error, t))
            self.logger.error(error_msg, exc_info=error)
            raise ReporterError(error_msg) from error

    @staticmethod
    def _extract_suite_metrics(suites) -> SuiteMetrics:
        metrics = SuiteMetrics()
        match suites:
            case JestJUnitXmlTestSuites() | NextestJUnitXmlTestSuites():
                metrics.time = suites.time
                metrics.tests = suites.tests
                metrics.failure = suites.failures + suites.errors
                metrics.skipped = sum(suite.skipped for suite in suites.test_suites)
            case MochaJUnitXmlTestSuites():
                metrics.time = suites.time
                # Mocha test reporting has been known to inaccurately total the number of
                # tests at the top level, so we count the number of test cases
                metrics.tests = (
                    sum(len(suite.test_cases) for suite in suites.test_suites if suite.test_cases)
                    if suites.test_suites
                    else 0
                )
                metrics.failure = suites.failures
                metrics.skipped = suites.skipped or 0
            case PlaywrightJUnitXmlTestSuites():
                metrics.time = suites.time
                metrics.tests = suites.tests
                metrics.failure = suites.failures + suites.errors
                metrics.skipped = suites.skipped
                metrics.fixme = sum(
                    1
                    for suite in suites.test_suites
                    for case in suite.test_cases
                    if case.properties and any(p.name == "fixme" for p in case.properties.property)
                )
                # An assumption is made that the presence of a nested system-out tag in
                # a test case that contains a link to a trace.zip attachment file as
                # content is the result of a retry.
                metrics.retry = sum(
                    1
                    for suite in suites.test_suites
                    for case in suite.test_cases
                    if case.system_out and "trace.zip" in case.system_out
                )
            case PytestJUnitXmlTestSuites():
                metrics.time = sum(suite.time for suite in suites.test_suites)
                metrics.tests = sum(suite.tests for suite in suites.test_suites)
                metrics.failure = sum(
                    suite.failures + suite.errors for suite in suites.test_suites
                )
                metrics.skipped = sum(suite.skipped for suite in suites.test_suites)
            case TapJUnitXmlTestSuites():
                metrics.tests = sum(suite.tests for suite in suites.test_suites)
                # With Tap it's possible for errors to be omitted
                metrics.failure = sum(
                    suite.failures + (suite.errors or 0) for suite in suites.test_suites
                )
        return metrics

    def _parse_results(
        self, artifacts_list: list[JUnitXmlJobTestSuites] | None
    ) -> list[SuiteReporterResult]:
        results: list[SuiteReporterResult] = []
        if not artifacts_list:
            return results

        for artifact in artifacts_list:
            test_suite_result = SuiteReporterResult(
                repository=self.repository,
                workflow=self.workflow,
                test_suite=self.test_suite,
                timestamp=artifact.job_timestamp,
                date=self._extract_date(artifact.job_timestamp),
                job=artifact.job,
            )

            times: list[float] = []
            for suites in artifact.test_suites:
                suite_metrics: SuiteMetrics = self._extract_suite_metrics(suites)
                if suite_metrics.time:
                    times.append(suite_metrics.time)
                test_suite_result.failure += suite_metrics.failure
                test_suite_result.skipped += suite_metrics.skipped
                test_suite_result.success += suite_metrics.success
                test_suite_result.fixme += suite_metrics.fixme
                test_suite_result.retry += suite_metrics.retry

            # Times are not always available, for example with TAP.
            # Times at the suites, suite and case level may not sum-up to the same values. This can
            # be due to many factors including the use of threads.
            test_suite_result.run_time = sum(times)
            test_suite_result.execution_time = max(times) if times else 0

            results.append(test_suite_result)

        # Sort by timestamp and then by job
        sorted_results = sorted(results, key=lambda result: (result.timestamp, result.job))

        return sorted_results
