# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""Module for test configurations for the Metric Reporter."""

from pathlib import Path

import pytest
from pydantic import BaseModel

from scripts.metric_reporter.parser.coverage_json_parser import (
    LlvmCovReport,
    PytestReport,
    PytestMeta,
    PytestTotals,
    LlvmCovDataItem,
    LlvmCovStats,
    LlvmCovTotals,
)
from scripts.metric_reporter.reporter.coverage_reporter import CoverageReporterResult

LLVM_COV_SAMPLE_DIRECTORY = "llvm_cov_json_samples"
LLVM_COV_REPORT_LIST: list[LlvmCovReport | PytestReport] = [
    LlvmCovReport(
        job_number=1,
        job_timestamp="2024-08-30T19:56:50Z",
        data=[
            LlvmCovDataItem(
                totals=LlvmCovTotals(
                    branches=LlvmCovStats(count=0, covered=0, percent=0.0),
                    functions=LlvmCovStats(count=1007, covered=589, percent=58.490566037735846),
                    instantiations=LlvmCovStats(
                        count=4773, covered=1088, percent=22.79488791116698
                    ),
                    lines=LlvmCovStats(count=9441, covered=5761, percent=61.0210782756064),
                    mcdc=LlvmCovStats(count=0, covered=0, percent=0.0),
                    regions=LlvmCovStats(count=5021, covered=2340, percent=46.60426209918343),
                )
            )
        ],
        type="llvm.coverage.json.export",
        version="2.0.1",
    )
]
LLVM_COV_REPORT_RESULTS: list[CoverageReporterResult] = [
    CoverageReporterResult(
        repository="repo",
        workflow="main",
        test_suite="suite",
        date="2024-08-30",
        timestamp="2024-08-30T19:56:50Z",
        job=1,
        line_count=9441,
        line_covered=5761,
        line_not_covered=3680,
        line_excluded=None,
        line_percent=61.0210782756064,
        function_count=1007,
        function_covered=589,
        function_not_covered=418,
        function_percent=58.490566037735846,
        branch_count=0,
        branch_covered=0,
        branch_not_covered=0,
        branch_percent=0.0,
    )
]
LLVM_COV_CSV: str = (
    "Repository,Workflow,Test Suite,Date,Timestamp,Job Number,Line Count,Line Covered,Line Not Covered,Line Excluded,Line Percent,Function Count,Function Covered,Function Not Covered,Function Percent,Branch Count,Branch Covered,Branch Not Covered,Branch Percent\r\n"
    "repo,main,suite,2024-08-30,2024-08-30T19:56:50Z,1,9441,5761,3680,,61.0210782756064,1007,589,418,58.490566037735846,0,0,0,0.0\r\n"
)

PYTEST_SAMPLE_DIRECTORY = "pytest_json_samples"
PYTEST_REPORT_LIST: list[LlvmCovReport | PytestReport] = [
    PytestReport(
        job_number=1,
        job_timestamp=None,
        meta=PytestMeta(
            format=2,
            version="7.5.4",
            timestamp="2024-08-29T17:43:41.679830",
            branch_coverage=True,
            show_contexts=False,
        ),
        totals=PytestTotals(
            num_statements=3782,
            covered_lines=3138,
            missing_lines=644,
            excluded_lines=217,
            percent_covered=82.01058201058201,
            percent_covered_display="82",
            num_branches=943,
            covered_branches=737,
            num_partial_branches=34,
            missing_branches=206,
        ),
    )
]
PYTEST_REPORT_RESULTS: list[CoverageReporterResult] = [
    CoverageReporterResult(
        repository="repo",
        workflow="main",
        test_suite="suite",
        date="2024-08-29",
        timestamp="2024-08-29T17:43:41.679830",
        job=1,
        line_count=3782,
        line_covered=3138,
        line_not_covered=644,
        line_excluded=217,
        line_percent=82.01058201058201,
        branch_count=943,
        branch_covered=737,
        branch_not_covered=206,
        branch_percent=78.15482502651113,
    )
]
PYTEST_CSV: str = (
    "Repository,Workflow,Test Suite,Date,Timestamp,Job Number,Line Count,Line Covered,Line Not Covered,Line Excluded,Line Percent,Function Count,Function Covered,Function Not Covered,Function Percent,Branch Count,Branch Covered,Branch Not Covered,Branch Percent\r\n"
    "repo,main,suite,2024-08-29,2024-08-29T17:43:41.679830,1,3782,3138,644,217,82.01058201058201,,,,,943,737,206,78.15482502651113\r\n"
)


class SampleCoverageData(BaseModel):
    """Grouping of test coverage sample data."""

    sample_directory: Path
    report_list: list[LlvmCovReport | PytestReport]
    report_results: list[CoverageReporterResult]
    csv: str


@pytest.fixture
def test_data_directory() -> Path:
    """Provide the base path to the test data directory."""
    return Path(__file__).parent / "test_data"


@pytest.fixture
def coverage_llvm_cov_data(test_data_directory: Path) -> SampleCoverageData:
    """Provide the llvm-cov coverage report sample data."""
    return SampleCoverageData(
        sample_directory=test_data_directory / LLVM_COV_SAMPLE_DIRECTORY,
        report_list=LLVM_COV_REPORT_LIST,
        report_results=LLVM_COV_REPORT_RESULTS,
        csv=LLVM_COV_CSV,
    )


@pytest.fixture
def coverage_pytest_data(test_data_directory: Path) -> SampleCoverageData:
    """Provide the pytest coverage report sample data."""
    return SampleCoverageData(
        sample_directory=test_data_directory / PYTEST_SAMPLE_DIRECTORY,
        report_list=PYTEST_REPORT_LIST,
        report_results=PYTEST_REPORT_RESULTS,
        csv=PYTEST_CSV,
    )
