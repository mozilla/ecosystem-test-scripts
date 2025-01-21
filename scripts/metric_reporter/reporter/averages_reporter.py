# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""Module for reporting test suite average results from JUnit XML reports."""

import operator
from datetime import date, datetime, timedelta
from functools import reduce
from typing import Any, Sequence

from google.api_core.exceptions import GoogleAPIError
from google.cloud.bigquery import Client, QueryJobConfig, ScalarQueryParameter

from scripts.metric_reporter.constants import DATE_FORMAT
from scripts.metric_reporter.reporter.base_reporter import (
    BaseReporter,
    ReporterError,
    ReporterResultBase,
)
from scripts.metric_reporter.reporter.suite_reporter import SuiteReporterResult, Status

DAYS_1: int = 1
DAYS_30: int = 30
DAYS_60: int = 60
DAYS_90: int = 90


class AveragesReporterResult(ReporterResultBase):
    """Represents the average results of test suite runs for a repository."""

    repository: str
    workflow: str
    test_suite: str
    start_date_30: str
    stop_date_30: str
    suite_count_30: int
    success_rate_30: float | None = None
    run_time_30: float | None = None
    execution_time_30: float | None = None
    start_date_60: str
    stop_date_60: str
    suite_count_60: int
    success_rate_60: float | None = None
    run_time_60: float | None = None
    execution_time_60: float | None = None
    start_date_90: str
    stop_date_90: str
    suite_count_90: int
    success_rate_90: float | None = None
    run_time_90: float | None = None
    execution_time_90: float | None = None

    def dict_with_fieldnames(self) -> dict[str, Any]:
        """Convert the averages result to a dictionary with field names.

        Returns:
            dict[str, Any]: Dictionary representation of the test suite averages result.
        """
        return {
            "Repository": self.repository,
            "Workflow": self.workflow,
            "Test Suite": self.test_suite,
            "Start Date 30": self.start_date_30,
            "End Date 30": self.stop_date_30,
            "Suite Count 30": self.suite_count_30,
            "Success Rate 30": self.success_rate_30,
            "Run Time 30": self.run_time_30,
            "Execution Time 30": self.execution_time_30,
            "Start Date 60": self.start_date_60,
            "End Date 60": self.stop_date_60,
            "Suite Count 60": self.suite_count_60,
            "Success Rate 60": self.success_rate_60,
            "Run Time 60": self.run_time_60,
            "Execution Time 60": self.execution_time_60,
            "Start Date 90": self.start_date_90,
            "End Date 90": self.stop_date_90,
            "Suite Count 90": self.suite_count_90,
            "Success Rate 90": self.success_rate_90,
            "Run Time 90": self.run_time_90,
            "Execution Time 90": self.execution_time_90,
        }


class AveragesReporter(BaseReporter):
    """Handles the reporting of test suite results from JUnit XML Reports."""

    def __init__(
        self,
        repository: str,
        workflow: str,
        test_suite: str,
        suite_results: Sequence[SuiteReporterResult],
    ) -> None:
        """Initialize the reporter with the test suite results.

        Args:
            repository (str): The repository associated to the test suite.
            workflow (str): The workflow associated to the test suite.
            test_suite (str): The test suite name.
            suite_results (Sequence[SuiteReporterResult]): Test suite results.
        """
        super().__init__()
        self.repository = repository
        self.workflow = workflow
        self.test_suite = test_suite
        self.results: list[AveragesReporterResult] = self._parse_results(suite_results)

    def update_table(self, client: Client, project_id: str, dataset_name: str) -> None:
        """Update the BigQuery table.

        Args:
            client: The client to interact with BigQuery.
            project_id (str): The BigQuery project ID.
            dataset_name (str): The BigQuery dataset name.
        """
        table_id = f"{project_id}.{dataset_name}.{self.repository}_averages"

        if not self.results:
            self.logger.warning(
                f"There are no averages for {self.repository}/{self.workflow}/{self.test_suite} to "
                f"add to {table_id}."
            )
            return

        last_update: date | None = self._get_last_update(client, table_id)

        # If no 'last_update' insert all results, else insert results that occur after the last
        # update end date
        new_results: list[AveragesReporterResult] = (
            self.results
            if not last_update
            else [
                r
                for r in self.results
                if datetime.strptime(r.stop_date_30, DATE_FORMAT).date() > last_update
                or datetime.strptime(r.stop_date_60, DATE_FORMAT).date() > last_update
                or datetime.strptime(r.stop_date_90, DATE_FORMAT).date() > last_update
            ]
        )
        if not new_results:
            self.logger.warning(
                f"There are no new averages for {self.repository}/{self.workflow}/{self.test_suite}"
                f" to add to {table_id}."
            )
            return

        self._insert_rows(client, table_id, new_results)

    def _check_rows_exist(
        self, client: Client, table_id: str, results: Sequence[AveragesReporterResult]
    ) -> bool:
        conditions = []
        query_parameters = []
        for index, result in enumerate(results):
            prefix = f"p{index}"
            conditions.append(
                f"""(
                    Repository = @{prefix}_repository
                    AND Workflow = @{prefix}_workflow
                    AND `Test Suite` = @{prefix}_test_suite
                    AND `End Date 30` = @{prefix}_end_date_30
                    AND `End Date 60` = @{prefix}_end_date_60
                    AND `End Date 90` = @{prefix}_end_date_90
                )"""
            )
            query_parameters.extend(
                [
                    ScalarQueryParameter(f"{prefix}_repository", "STRING", result.repository),
                    ScalarQueryParameter(f"{prefix}_workflow", "STRING", result.workflow),
                    ScalarQueryParameter(f"{prefix}_test_suite", "STRING", result.test_suite),
                    ScalarQueryParameter(f"{prefix}_end_date_30", "DATE", result.stop_date_30),
                    ScalarQueryParameter(f"{prefix}_end_date_60", "DATE", result.stop_date_60),
                    ScalarQueryParameter(f"{prefix}_end_date_90", "DATE", result.stop_date_90),
                ]
            )
        where_clause = " OR ".join(conditions)
        query = f"""
            SELECT 1
            FROM `{table_id}`
            WHERE {where_clause}
            LIMIT 1
        """  # nosec
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

    def _get_last_update(self, client: Client, table_id: str) -> date | None:
        query = f"""
            SELECT GREATEST(MAX(`End Date 30`), MAX(`End Date 60`), MAX(`End Date 90`)) as last_update 
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
                last_update: date | None = row["last_update"]
                return last_update
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
        self, client: Client, table_id: str, results: list[AveragesReporterResult]
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
                f"Inserted {len(results)} averages from "
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
        suite_results: Sequence[SuiteReporterResult],
    ) -> list[AveragesReporterResult]:
        results: list[AveragesReporterResult] = []
        if not suite_results:
            return results

        # Assumes that suite_results is sorted
        first_date: str | None = suite_results[0].date
        last_date: str | None = suite_results[-1].date
        # Adjust last_date if it's today's date, all the information for the day may not be
        # available to calculate a proper average.
        if (
            last_date
            and last_date == datetime.now().strftime(DATE_FORMAT)
            and len(suite_results) > 1
        ):
            last_date = suite_results[-2].date

        if not first_date or not last_date:
            return results

        first_datetime: datetime = datetime.strptime(first_date, DATE_FORMAT)
        last_datetime: datetime = datetime.strptime(last_date, DATE_FORMAT)

        while last_datetime >= first_datetime + timedelta(days=DAYS_30):
            averages_result_dict: dict[str, Any] = {
                "repository": self.repository,
                "workflow": self.workflow,
                "test_suite": self.test_suite,
                **self._calculate_averages(suite_results, last_datetime, DAYS_30),
                **self._calculate_averages(suite_results, last_datetime, DAYS_60),
                **self._calculate_averages(suite_results, last_datetime, DAYS_90),
            }
            results.append(AveragesReporterResult(**averages_result_dict))
            last_datetime -= timedelta(days=DAYS_1)
        results.reverse()  # Reverse the list to get chronological order
        return results

    @staticmethod
    def _calculate_averages(
        results: Sequence[SuiteReporterResult], stop_date: datetime, delta: int
    ) -> dict[str, Any]:
        start_date: datetime = stop_date - timedelta(days=delta)
        subset: list[SuiteReporterResult] = [
            r
            for r in results
            if r.date and start_date <= datetime.strptime(r.date, DATE_FORMAT) <= stop_date
        ]
        suite_count: int = len(subset)
        averages: dict[str, Any] = {
            f"start_date_{str(delta)}": start_date.strftime(DATE_FORMAT),
            f"stop_date_{str(delta)}": stop_date.strftime(DATE_FORMAT),
            f"suite_count_{str(delta)}": suite_count,
        }

        if suite_count > 0:
            averages[f"success_rate_{str(delta)}"] = (
                len([r for r in subset if r.status == Status.SUCCESS]) / suite_count * 100
            )

            run_times: list[float] = [r.run_time for r in subset if r.run_time > 0]
            if run_times:
                averages[f"run_time_{str(delta)}"] = reduce(operator.add, run_times) / suite_count

            execution_times: list[float] = [r.execution_time for r in subset if r.execution_time]
            if execution_times:
                averages[f"execution_time_{str(delta)}"] = (
                    reduce(operator.add, execution_times) / suite_count
                )

        return averages
