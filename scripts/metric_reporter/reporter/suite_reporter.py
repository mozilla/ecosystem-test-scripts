# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""Module for reporting test suite results from CircleCI metadata."""

from datetime import datetime
from enum import Enum
from typing import Any, Sequence

from google.api_core.exceptions import GoogleAPIError
from google.cloud.bigquery import ArrayQueryParameter, Client, QueryJobConfig, ScalarQueryParameter

from scripts.metric_reporter.constants import DATE_FORMAT, DATETIME_FORMAT
from scripts.metric_reporter.parser.circleci_json_parser import CircleCIJobTestMetadata
from scripts.metric_reporter.parser.junit_xml_parser import JUnitXmlJobTestSuites
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
    UNKNOWN = "unknown"


class SuiteReporterResult(ReporterResultBase):
    """Represents the results of a test suite run."""

    repository: str
    workflow: str
    test_suite: str

    # The timestamp between CI and JUnit XML is likely to be different since they represent job
    # start and test start respectively
    timestamp: str | None = None

    date: str | None = None
    job: int

    @property
    def status(self) -> Status:
        """Test Suite status"""
        # Note the CircleCI JSON has a status field, but it reflects the job status which may fail
        # for reasons other than test failure
        if self.failure > 0:
            return Status.FAILED
        if self.unknown > 0:
            return Status.UNKNOWN
        return Status.SUCCESS

    # The summation of all test run times in seconds. Parallelization is not taken into
    # consideration.
    run_time: float = 0

    # JUnit XML only. Equal to the longest run_time in seconds when tests are run in parallel.
    # We know tests are run in parallel if we have multiple reports for a
    # repository/workflow/test_suite
    execution_time: float | None = None

    # CI only. The amount of time for the test CI Job in seconds.
    job_time: float | None = None

    success: int = 0
    failure: int = 0
    skipped: int = 0

    # JUnit XML only. An annotation available in Playwright only. Subset of 'skipped'.
    fixme: int = 0

    # CI only. When CircleCI fails to classify a test as 'success', 'failure' or 'skipped' it is set
    # to unknown.
    unknown: int = 0

    # JUnit XML only. The number of tests that were the result of a re-execution. It is possible
    # that the same test is re-executed more than once.
    retry: int = 0

    @property
    def total(self) -> int:
        """Calculate the total number of tests."""
        return self.success + self.failure + self.skipped + self.unknown

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

    @property
    def unknown_rate(self) -> float | None:
        """Calculate the unknown rate of the test suite."""
        return self._calculate_rate(self.unknown, self.total)

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
            "Job Time": self.job_time,
            "Run Time": self.run_time,
            "Success": self.success,
            "Failure": self.failure,
            "Skipped": self.skipped,
            "Fixme": self.fixme,
            "Unknown": self.unknown,
            "Retry Count": self.retry,
            "Total": self.total,
            "Success Rate": self.success_rate,
            "Failure Rate": self.failure_rate,
            "Skipped Rate": self.skipped_rate,
            "Fixme Rate": self.fixme_rate,
            "Unknown Rate": self.unknown_rate,
        }


class SuiteReporter(BaseReporter):
    """Handles the reporting of test suite results from CircleCI metadata and JUnit XML Reports."""

    def __init__(
        self,
        repository: str,
        workflow: str,
        test_suite: str,
        metadata_list: list[CircleCIJobTestMetadata] | None,
        junit_artifact_list: list[JUnitXmlJobTestSuites] | None,
    ) -> None:
        """Initialize the reporter with the directory containing test result data.

        Args:
            repository (str): The repository associated to the test suite.
            workflow (str): The workflow associated to the test suite.
            test_suite (str): The test suite name.
            metadata_list (list[CircleCIJobTestMetadata] | None): The metadata from CircleCI test
                                                                  jobs.
            junit_artifact_list (list[JUnitXmlJobTestSuites] | None): The test results from JUnit
                                                                      XML artifacts.
        """
        super().__init__()
        self.repository = repository
        self.workflow = workflow
        self.test_suite = test_suite
        self.results: Sequence[SuiteReporterResult] = self._parse_results(
            metadata_list, junit_artifact_list
        )

    def update_table(self, client: Client, project_id: str, dataset_name: str) -> None:
        """Update the BigQuery table with new results.

        Args:
            client (Client): The BigQuery client to interact with BigQuery.
            project_id (str): The BigQuery project ID.
            dataset_name (str): The BigQuery dataset name.
        """
        table_id = f"{project_id}.{dataset_name}.{self.repository}_results"

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

    def _parse_results(
        self,
        metadata_list: list[CircleCIJobTestMetadata] | None,
        artifacts_list: list[JUnitXmlJobTestSuites] | None,
    ) -> list[SuiteReporterResult]:
        metadata_results_dict: dict[int, SuiteReporterResult] = {}
        if metadata_list:
            metadata_results_dict = self._parse_metadata(metadata_list)

        artifact_results_dict: dict[int, SuiteReporterResult] = {}
        if artifacts_list:
            artifact_results_dict = self._parse_artifacts(artifacts_list)

        # Reconcile data preferring artifact results except for date, timestamp and
        # job_time from metadata
        results: list[SuiteReporterResult] = []
        for job_number, artifact_result in artifact_results_dict.items():
            metadata_result = metadata_results_dict.pop(job_number, None)
            if metadata_result:
                self._check_for_mismatch(artifact_result, metadata_result)
                artifact_result.date = metadata_result.date
                artifact_result.timestamp = metadata_result.timestamp
                artifact_result.job_time = metadata_result.job_time
            results.append(artifact_result)

        # Add remaining metadata results that were not matched
        results.extend(metadata_results_dict.values())

        # Sort by timestamp and then by job
        sorted_results = sorted(results, key=lambda result: (result.timestamp, result.job))

        return sorted_results

    def _parse_metadata(
        self, metadata_list: list[CircleCIJobTestMetadata]
    ) -> dict[int, SuiteReporterResult]:
        results: dict[int, SuiteReporterResult] = {}
        for metadata in metadata_list:
            if not metadata.test_metadata or metadata.job.status == CANCELED_JOB_STATUS:
                continue

            if metadata.job.status == RUNNING_JOB_STATUS:
                self.logger.warning(
                    f"Files from job "
                    f"{self.repository}/{self.workflow}/{self.test_suite}/{metadata.job.job_number}"
                    " are incomplete. Please delete them and re-scrape."
                )
                continue

            started_at = datetime.strptime(metadata.job.started_at, DATETIME_FORMAT)
            stopped_at = datetime.strptime(metadata.job.stopped_at, DATETIME_FORMAT)
            job_time = (stopped_at - started_at).total_seconds()
            test_suite_result = SuiteReporterResult(
                repository=self.repository,
                workflow=self.workflow,
                test_suite=self.test_suite,
                job=metadata.job.job_number,
                date=started_at.strftime(DATE_FORMAT),
                timestamp=metadata.job.started_at,
                job_time=job_time,
            )

            run_time: float = 0
            for test in metadata.test_metadata:
                run_time += test.run_time
                if test.result in SUCCESS_RESULTS:
                    test_suite_result.success += 1
                elif test.result == FAILURE_RESULT:
                    test_suite_result.failure += 1
                elif test.result == SKIPPED_RESULT:
                    test_suite_result.skipped += 1
                else:
                    test_suite_result.unknown += 1
            test_suite_result.run_time = round(run_time, 3)

            results[metadata.job.job_number] = test_suite_result
        return results

    def _parse_artifacts(
        self, artifacts_list: list[JUnitXmlJobTestSuites]
    ) -> dict[int, SuiteReporterResult]:
        results: dict[int, SuiteReporterResult] = {}
        for artifact in artifacts_list:
            test_suite_result = SuiteReporterResult(
                repository=self.repository,
                workflow=self.workflow,
                test_suite=self.test_suite,
                job=artifact.job,
            )

            run_times: list[float] = []
            execution_times: list[float] = []
            for suites in artifact.test_suites:
                # Update date and timestamp at the test_suites level if not already set
                if not test_suite_result.date and suites.timestamp:
                    test_suite_result.timestamp = suites.timestamp
                    test_suite_result.date = self._extract_date(suites.timestamp)
                run_time: float = 0
                # A top level test_suites time is not always available. The top level time may
                # not be equal to the sum of the test case times due to the use of threads/workers.
                execution_time: float | None = (
                    suites.time if suites.time and suites.time > 0 else None
                )
                for suite in suites.test_suites:
                    # Update date and timestamp at the test_suite level if not already set
                    if not test_suite_result.date and suite.timestamp:
                        test_suite_result.timestamp = suite.timestamp
                        test_suite_result.date = self._extract_date(suite.timestamp)

                    # Mocha test reporting has been known to inaccurately total the number of tests
                    # in the 'tests' attribute, so we count the number of test cases
                    tests = len(suite.test_cases)
                    skipped = suite.skipped if suite.skipped else 0
                    test_suite_result.failure += suite.failures
                    test_suite_result.skipped += skipped
                    test_suite_result.success += tests - suite.failures - skipped

                    for case in suite.test_cases:
                        # Summing the time for each test case if test_suite.time is not available
                        if case.time:
                            run_time += case.time

                        # Increment "fixme" count, Playwright only
                        if case.properties and any(p.name == "fixme" for p in case.properties):
                            test_suite_result.fixme += 1

                        # Check for retry condition, Playwright only
                        # An assumption is made that the presence of a nested system-out tag in a
                        # test case that contains a link to a trace.zip attachment file as content
                        # is the result of a retry.
                        if (
                            case.system_out
                            and case.system_out.text
                            and "trace.zip" in case.system_out.text
                        ):
                            test_suite_result.retry += 1

                run_times.append(run_time)
                # If a time at the test suites level is not provided, then use the summation of
                # times at the test case level, or run_time.
                execution_times.append(execution_time if execution_time is not None else run_time)

            test_suite_result.run_time = round(sum(run_times), 3)
            test_suite_result.execution_time = round(max(execution_times), 3)
            results[artifact.job] = test_suite_result

        return results

    def _check_for_mismatch(
        self, artifact_result: SuiteReporterResult, metadata_result: SuiteReporterResult
    ) -> None:
        excluded_field_set = {
            "job",
            "repository",
            "workflow",
            "test_suite",
            "timestamp",
            "execution_time",
            "job_time",
            "fixme",
            "retry",
        }
        artifact_data: dict[str, Any] = {
            f: v for f, v in artifact_result.model_dump().items() if f not in excluded_field_set
        }
        metadata_data: dict[str, Any] = {
            f: v for f, v in metadata_result.model_dump().items() if f not in excluded_field_set
        }
        mismatches: dict[str, Any] = {
            f: (artifact_data[f], metadata_data.get(f))
            for f in artifact_data
            if artifact_data[f] != metadata_data.get(f)
        }
        if mismatches:
            self.logger.warning(
                f"Mismatches detected for {artifact_result.repository}/{artifact_result.workflow}/"
                f"{artifact_result.test_suite}/{artifact_result.job}, executed on "
                f"{artifact_result.timestamp}:\n"
                f"Mismatched Fields: {mismatches}"
            )
