# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""Module for reporting test suite average results from CircleCI metadata."""

import operator
from datetime import datetime, timedelta
from functools import reduce
from typing import Any, Sequence

from scripts.metric_reporter.base_reporter import BaseReporter, ReporterResultBase, DATE_FORMAT
from scripts.metric_reporter.suite_reporter import SuiteReporterResult, Status

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
    job_time_30: float | None = None
    execution_time_30: float | None = None
    start_date_60: str
    stop_date_60: str
    suite_count_60: int
    success_rate_60: float | None = None
    run_time_60: float | None = None
    job_time_60: float | None = None
    execution_time_60: float | None = None
    start_date_90: str
    stop_date_90: str
    suite_count_90: int
    success_rate_90: float | None = None
    run_time_90: float | None = None
    job_time_90: float | None = None
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
            "Job Time 30": self.job_time_30,
            "Start Date 60": self.start_date_60,
            "End Date 60": self.stop_date_60,
            "Suite Count 60": self.suite_count_60,
            "Success Rate 60": self.success_rate_60,
            "Run Time 60": self.run_time_60,
            "Execution Time 60": self.execution_time_60,
            "Job Time 60": self.job_time_60,
            "Start Date 90": self.start_date_90,
            "End Date 90": self.stop_date_90,
            "Suite Count 90": self.suite_count_90,
            "Success Rate 90": self.success_rate_90,
            "Run Time 90": self.run_time_90,
            "Execution Time 90": self.execution_time_90,
            "Job Time 90": self.job_time_90,
        }


class AveragesReporter(BaseReporter):
    """Handles the reporting of test suite results from CircleCI metadata and JUnit XML Reports."""

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
        self.results = self._parse_results(repository, workflow, test_suite, suite_results)

    def _parse_results(
        self,
        repository: str,
        workflow: str,
        test_suite: str,
        suite_results: Sequence[SuiteReporterResult],
    ) -> list[AveragesReporterResult]:
        results: list[AveragesReporterResult] = []
        if not suite_results:
            return results

        # Assumes that suite_results is sorted
        first_date: str | None = suite_results[0].date
        last_date: str | None = suite_results[-1].date
        if not first_date or not last_date:
            return results

        first_datetime: datetime = datetime.strptime(first_date, DATE_FORMAT)
        last_datetime: datetime = datetime.strptime(last_date, DATE_FORMAT)

        while last_datetime >= first_datetime + timedelta(days=DAYS_30):
            averages_result_dict: dict[str, Any] = {
                "repository": repository,
                "workflow": workflow,
                "test_suite": test_suite,
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

            job_times: list[float] = [r.job_time for r in subset if r.job_time]
            if job_times:
                averages[f"job_time_{str(delta)}"] = reduce(operator.add, job_times) / suite_count

            execution_times: list[float] = [r.execution_time for r in subset if r.execution_time]
            if execution_times:
                averages[f"execution_time_{str(delta)}"] = (
                    reduce(operator.add, execution_times) / suite_count
                )

        return averages
