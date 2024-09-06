# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""Module for reporting test suite coverage results."""

from typing import Any, Sequence

from scripts.metric_reporter.parser.coverage_json_parser import (
    LlvmCovReport,
    LlvmCovTotals,
    PytestMeta,
    PytestReport,
    PytestTotals,
)
from scripts.metric_reporter.reporter.base_reporter import (
    BaseReporter,
    ReporterResultBase,
    ReporterError,
)


class CoverageReporterResult(ReporterResultBase):
    """Represents the coverage of a test suite run."""

    repository: str
    workflow: str
    test_suite: str

    # llvm-cov doesn't have a timestamp as part of their report, so timestamp and date may not be
    # available if CircleCI can't be used to fill in the gap
    date: str | None = None
    timestamp: str | None = None

    job: int
    line_count: int | None
    line_covered: int | None
    line_not_covered: int | None
    line_excluded: int | None = None  # pytest only
    line_percent: float | None
    function_count: int | None = None  # llvm-cov only
    function_covered: int | None = None  # llvm-cov only
    function_not_covered: int | None = None  # llvm-cov only
    function_percent: float | None = None  # llvm-cov only
    branch_count: int | None
    branch_covered: int | None
    branch_not_covered: int | None
    branch_percent: float | None

    def dict_with_fieldnames(self) -> dict[str, Any]:
        """Convert the coverage result to a dictionary with field names.

        Returns:
            dict[str, Any]: Dictionary representation of the coverage result.
        """
        return {
            "Repository": self.repository,
            "Workflow": self.workflow,
            "Test Suite": self.test_suite,
            "Date": self.date,
            "Timestamp": self.timestamp,
            "Job Number": self.job,
            "Line Count": self.line_count,
            "Line Covered": self.line_covered,
            "Line Not Covered": self.line_not_covered,
            "Line Excluded": self.line_excluded,
            "Line Percent": self.line_percent,
            "Function Count": self.function_count,
            "Function Covered": self.function_covered,
            "Function Not Covered": self.function_not_covered,
            "Function Percent": self.function_percent,
            "Branch Count": self.branch_count,
            "Branch Covered": self.branch_covered,
            "Branch Not Covered": self.branch_not_covered,
            "Branch Percent": self.branch_percent,
        }


class CoverageReporter(BaseReporter):
    """Handles the reporting of coverage results."""

    def __init__(
        self,
        repository: str,
        workflow: str,
        test_suite: str,
        coverage_artifact_list: list[LlvmCovReport | PytestReport] | None,
    ) -> None:
        """Initialize the reporter with the coverage data.

        Args:
            repository (str): The repository associated to the test suite.
            workflow (str): The workflow associated to the test suite.
            test_suite (str): The test suite name.
            coverage_artifact_list (list[LlvmCovReport | PytestReport]): The coverage report data
                                                                         from test suites.
        """
        super().__init__()
        self.results: Sequence[CoverageReporterResult] = self._parse_results(
            repository, workflow, test_suite, coverage_artifact_list
        )

    def _parse_results(
        self,
        repository: str,
        workflow: str,
        test_suite: str,
        coverage_artifact_list: list[LlvmCovReport | PytestReport] | None,
    ) -> Sequence[CoverageReporterResult]:
        if coverage_artifact_list is None:
            return []

        results: list[CoverageReporterResult] = []
        for artifact in coverage_artifact_list:
            if isinstance(artifact, LlvmCovReport):
                results.append(
                    self._parse_llvm_cov_report(repository, workflow, test_suite, artifact)
                )
            elif isinstance(artifact, PytestReport):
                results.append(
                    self._parse_pytest_report(repository, workflow, test_suite, artifact)
                )
            else:
                raise ReporterError(f"Unknown coverage type: {type(artifact)}")
        return results

    def _parse_llvm_cov_report(
        self, repository: str, workflow: str, test_suite: str, llvm_cov_report: LlvmCovReport
    ) -> CoverageReporterResult:
        if not len(llvm_cov_report.data) == 1:
            raise ReporterError(
                f"The coverage report for {repository}-{workflow}-{test_suite} has an unexpected "
                f"number of items in 'data'."
            )
        totals: LlvmCovTotals = llvm_cov_report.data[0].totals
        return CoverageReporterResult(
            repository=repository,
            workflow=workflow,
            test_suite=test_suite,
            timestamp=llvm_cov_report.job_timestamp,
            date=(
                self._extract_date(llvm_cov_report.job_timestamp)
                if llvm_cov_report.job_timestamp
                else None
            ),
            job=llvm_cov_report.job_number,
            line_count=totals.lines.count,
            line_covered=totals.lines.covered,
            line_not_covered=totals.lines.count - totals.lines.covered,
            line_percent=totals.lines.percent,
            function_count=totals.functions.count,
            function_covered=totals.functions.covered,
            function_not_covered=totals.functions.count - totals.functions.covered,
            function_percent=totals.functions.percent,
            branch_count=totals.branches.count,
            branch_covered=totals.branches.covered,
            branch_not_covered=totals.branches.count - totals.branches.covered,
            branch_percent=totals.branches.percent,
        )

    def _parse_pytest_report(
        self, repository: str, workflow: str, test_suite: str, pytest_report: PytestReport
    ) -> CoverageReporterResult:
        totals: PytestTotals = pytest_report.totals
        meta: PytestMeta = pytest_report.meta
        return CoverageReporterResult(
            repository=repository,
            workflow=workflow,
            test_suite=test_suite,
            timestamp=meta.timestamp,
            date=self._extract_date(meta.timestamp) if meta.timestamp else None,
            job=pytest_report.job_number,
            line_count=totals.num_statements,
            line_covered=totals.covered_lines,
            line_not_covered=totals.missing_lines,
            line_excluded=totals.excluded_lines,
            line_percent=totals.percent_covered,
            branch_count=totals.num_branches,
            branch_covered=totals.covered_branches,
            branch_not_covered=totals.missing_branches,
            branch_percent=(
                (totals.covered_branches / totals.num_branches) * 100
                if totals.num_branches
                else 0.0
            ),
        )
