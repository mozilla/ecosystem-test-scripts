# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""Module for reporting test suite results from CircleCI metadata."""

import csv
import logging
from datetime import datetime
from pathlib import Path

from pydantic import BaseModel

from scripts.common.error import BaseError
from scripts.test_metric_reporter.circleci_json_parser import CircleCIJsonParser

DATE_FORMAT = "%Y-%m-%d"
DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
SUCCESS_RESULTS = {"success", "system-out"}
FAILURE_RESULT = "failure"
SKIPPED_RESULT = "skipped"


class SuiteReporterResult(BaseModel):
    """Represents the results of a test suite run."""

    date: str
    job: int
    status: str
    execution_time: float  # in seconds
    success: int = 0
    failure: int = 0
    skipped: int = 0
    unknown: int = 0

    @property
    def date_job(self) -> str:
        """Combine the date and job number into a single string."""
        return f"{self.date} - {self.job}"

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
        return (value / total) * 100 if total > 0 else None

    def dict_with_fieldnames(self) -> dict[str, str | int | float | None]:
        """Convert the test suite result to a dictionary with field names.

        Returns:
            dict[str, str | int | float | None]: Dictionary representation of the test suite result.
        """
        return {
            "Date - Job Number": self.date_job,
            "Date": self.date,
            "Job Number": self.job,
            "Status": self.status,
            "Execution Time": self.execution_time,
            "Success": self.success,
            "Failure": self.failure,
            "Skipped": self.skipped,
            "Unknown": self.unknown,
            "Total": self.total,
            "Success Rate (%)": self.success_rate,
            "Failure Rate (%)": self.failure_rate,
            "Skipped Rate (%)": self.skipped_rate,
            "Unknown Rate (%)": self.unknown_rate,
        }


class SuiteReporterError(BaseError):
    """Exception raised for errors in the SuiteReporter."""

    pass


class SuiteReporter:
    """Handles the reporting of test suite results from CircleCI metadata."""

    logger = logging.getLogger(__name__)

    def __init__(self, test_metadata_directory: str) -> None:
        """Initialize the reporter with the directory containing test metadata.

        Args:
            test_metadata_directory (str): Path to the directory with CircleCI test metadata.

        Raises:
            CircleCIJsonParserError: If there is an error parsing the test metadata.
        """
        self._test_metadata_directory: str = test_metadata_directory
        self.metadata_results: list[SuiteReporterResult] = self._parse_circleci_metadata()

    def _parse_circleci_metadata(self) -> list[SuiteReporterResult]:
        results: list[SuiteReporterResult] = []
        circleci_parser = CircleCIJsonParser()
        for job_test_metadata in circleci_parser.parse(self._test_metadata_directory):
            if not job_test_metadata.test_metadata:
                continue

            started_at = datetime.strptime(job_test_metadata.job.started_at, DATETIME_FORMAT)
            stopped_at = datetime.strptime(job_test_metadata.job.stopped_at, DATETIME_FORMAT)
            execution_time = (stopped_at - started_at).total_seconds()
            test_suite_result = SuiteReporterResult(
                date=started_at.strftime(DATE_FORMAT),
                job=job_test_metadata.job.job_number,
                status=job_test_metadata.job.status,
                execution_time=execution_time,
            )

            for test in job_test_metadata.test_metadata:
                if test.result in SUCCESS_RESULTS:
                    test_suite_result.success += 1
                elif test.result == FAILURE_RESULT:
                    test_suite_result.failure += 1
                elif test.result == SKIPPED_RESULT:
                    test_suite_result.skipped += 1
                else:
                    test_suite_result.unknown += 1
            results.append(test_suite_result)
        return results

    def output_results_csv(self, report_path: str) -> None:
        """Output the test suite results to a CSV file.

        Args:
            report_path (str): Path to the file where the CSV report will be saved.

        Raises:
            SuiteReporterError: If the report file cannot be created or written to, or if
                                          there is an issue with the test data.
        """
        try:
            Path(report_path).parent.mkdir(parents=True, exist_ok=True)
            filtered_results: list[SuiteReporterResult] = [
                result for result in self.metadata_results if result.status != "canceled"
            ]
            if not filtered_results:
                self.logger.info("No data to write to the CSV file.")
                return

            fieldnames: list[str] = list(filtered_results[0].dict_with_fieldnames().keys())
            with open(report_path, "w", newline="") as csv_file:
                writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
                writer.writeheader()
                for result in filtered_results:
                    writer.writerow(result.dict_with_fieldnames())
        except (OSError, IOError) as error:
            error_mapping: dict[type, str] = {
                OSError: "Error creating directories for the report file",
                IOError: "The report file cannot be created or written to",
            }
            error_msg: str = error_mapping[type(error)]
            self.logger.error(error_msg, exc_info=error)
            raise SuiteReporterError(error_msg, error)
