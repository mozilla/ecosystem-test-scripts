# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""Module for test configurations for the Metric Reporter."""

from pathlib import Path
from typing import Any

import pytest
from pydantic import BaseModel

from scripts.metric_reporter.parser.coverage_json_parser import (
    CoverageJson,
    CoverageJsonGroup,
    LlvmCovDataItem,
    LlvmCovReport,
    LlvmCovStats,
    LlvmCovTotals,
    PytestReport,
    PytestMeta,
    PytestTotals,
)
from scripts.metric_reporter.parser.junit_xml_parser import (
    JestJUnitXmlTestSuites,
    JestJUnitXmlTestSuite,
    JestJUnitXmlTestCase,
    JUnitXmlGroup,
    JUnitXmlJobTestSuites,
    PlaywrightJUnitXmlFailure,
    PlaywrightJUnitXmlProperty,
    PlaywrightJUnitXmlTestSuites,
    PlaywrightJUnitXmlTestSuite,
    PlaywrightJUnitXmlTestCase,
    PytestJUnitXmlTestCase,
    PytestJUnitXmlTestSuite,
    PytestJUnitXmlTestSuites,
    PlaywrightJUnitXmlProperties,
)
from scripts.metric_reporter.reporter.coverage_reporter import CoverageReporterResult
from scripts.metric_reporter.reporter.suite_reporter import SuiteReporterResult

REPOSITORY = "repo"
WORKFLOW = "main"
TEST_SUITE = "suite"

JUNIT_XML_JOB_TEST_SUITES_LIST: list[JUnitXmlJobTestSuites] = [
    JUnitXmlJobTestSuites(
        job=1,
        job_timestamp="2024-01-01T00:00:00Z",
        test_suites=[
            PlaywrightJUnitXmlTestSuites(
                id="",
                name="",
                tests=1,
                failures=1,
                skipped=0,
                errors=0,
                time=1.1,
                test_suites=[
                    PlaywrightJUnitXmlTestSuite(
                        name="test_class",
                        timestamp="2024-01-01T00:00:00Z",
                        hostname="local",
                        tests=1,
                        failures=1,
                        skipped=0,
                        time=1.1,
                        errors=0,
                        test_cases=[
                            PlaywrightJUnitXmlTestCase(
                                name="test_failure",
                                classname="test_class",
                                time=1.1,
                                failure=PlaywrightJUnitXmlFailure(
                                    message="test_class:1:1 test_failure",
                                    type="FAILURE",
                                    text="\n                Error Msg\n            ",
                                ),
                                system_out=(
                                    "[[ATTACHMENT|../test_class/test_failure/trace.zip]]"
                                    "[[ATTACHMENT|../test_class/test_failure-retry1/trace.zip]]"
                                ),
                            )
                        ],
                    )
                ],
            )
        ],
    ),
    JUnitXmlJobTestSuites(
        job=2,
        job_timestamp="2024-01-02T00:00:00Z",
        test_suites=[
            PlaywrightJUnitXmlTestSuites(
                id="",
                name="",
                tests=1,
                failures=0,
                skipped=1,
                errors=0,
                time=1.2,
                test_suites=[
                    PlaywrightJUnitXmlTestSuite(
                        name="test_class",
                        timestamp="2024-01-02T00:00:00Z",
                        hostname="local",
                        tests=1,
                        failures=0,
                        skipped=1,
                        time=1.2,
                        errors=0,
                        test_cases=[
                            PlaywrightJUnitXmlTestCase(
                                name="test_fixme",
                                classname="test_class",
                                time=1.2,
                                properties=PlaywrightJUnitXmlProperties(
                                    property=[
                                        PlaywrightJUnitXmlProperty(
                                            name="fixme", value="see JIRA-0000"
                                        )
                                    ]
                                ),
                            )
                        ],
                    )
                ],
            )
        ],
    ),
    JUnitXmlJobTestSuites(
        job=3,
        job_timestamp="2024-01-03T00:00:00Z",
        test_suites=[
            PlaywrightJUnitXmlTestSuites(
                id="",
                name="",
                tests=1,
                failures=0,
                skipped=0,
                errors=0,
                time=1.3,
                test_suites=[
                    PlaywrightJUnitXmlTestSuite(
                        name="test_class",
                        timestamp="2024-01-03T00:00:00Z",
                        hostname="local",
                        tests=1,
                        failures=0,
                        skipped=0,
                        time=1.3,
                        errors=0,
                        test_cases=[
                            PlaywrightJUnitXmlTestCase(
                                name="test_retry",
                                classname="test_class",
                                time=1.3,
                                system_out="[[ATTACHMENT|../test_class/test_retry/trace.zip]]",
                            )
                        ],
                    )
                ],
            )
        ],
    ),
    JUnitXmlJobTestSuites(
        job=4,
        job_timestamp="2024-01-04T00:00:00Z",
        test_suites=[
            JestJUnitXmlTestSuites(
                name="",
                tests=1,
                failures=0,
                errors=0,
                time=1.4,
                test_suites=[
                    JestJUnitXmlTestSuite(
                        name="test_class",
                        timestamp="2024-01-04T00:00:00Z",
                        tests=1,
                        failures=0,
                        skipped=1,
                        time=1.4,
                        errors=0,
                        test_cases=[
                            JestJUnitXmlTestCase(
                                name="test_class",
                                classname="test_skipped",
                                time=1.4,
                            )
                        ],
                    )
                ],
            )
        ],
    ),
    JUnitXmlJobTestSuites(
        job=5,
        job_timestamp="2024-01-05T00:00:00Z",
        test_suites=[
            PytestJUnitXmlTestSuites(
                test_suites=[
                    PytestJUnitXmlTestSuite(
                        name="test_class",
                        timestamp="2024-01-05T00:00:00Z",
                        hostname="ip-10-0-175-52",
                        tests=1,
                        failures=0,
                        skipped=0,
                        time=1.5,
                        errors=0,
                        test_cases=[
                            PytestJUnitXmlTestCase(
                                name="test_class",
                                classname="test_success",
                                time=1.5,
                            )
                        ],
                    )
                ],
            )
        ],
    ),
]

ARTIFACT_RESULTS: list[SuiteReporterResult] = [
    SuiteReporterResult(
        repository=REPOSITORY,
        workflow=WORKFLOW,
        test_suite=TEST_SUITE,
        timestamp="2024-01-01T00:00:00Z",
        date="2024-01-01",
        job=1,
        run_time=1.1,
        execution_time=1.1,
        failure=1,
        retry=1,
    ),
    SuiteReporterResult(
        repository=REPOSITORY,
        workflow=WORKFLOW,
        test_suite=TEST_SUITE,
        timestamp="2024-01-02T00:00:00Z",
        date="2024-01-02",
        job=2,
        run_time=1.2,
        execution_time=1.2,
        skipped=1,
        fixme=1,
    ),
    SuiteReporterResult(
        repository=REPOSITORY,
        workflow=WORKFLOW,
        test_suite=TEST_SUITE,
        timestamp="2024-01-03T00:00:00Z",
        date="2024-01-03",
        job=3,
        run_time=1.3,
        execution_time=1.3,
        success=1,
        retry=1,
    ),
    SuiteReporterResult(
        repository=REPOSITORY,
        workflow=WORKFLOW,
        test_suite=TEST_SUITE,
        timestamp="2024-01-04T00:00:00Z",
        date="2024-01-04",
        job=4,
        run_time=1.4,
        execution_time=1.4,
        skipped=1,
    ),
    SuiteReporterResult(
        repository=REPOSITORY,
        workflow=WORKFLOW,
        test_suite=TEST_SUITE,
        timestamp="2024-01-05T00:00:00Z",
        date="2024-01-05",
        job=5,
        run_time=1.5,
        execution_time=1.5,
        success=1,
    ),
]
ARTIFACT_JSON: list[dict[str, Any]] = [
    {
        "Date": "2024-01-01",
        "Execution Time": 1.1,
        "Failure": 1,
        "Failure Rate": 100.0,
        "Fixme": 0,
        "Fixme Rate": 0.0,
        "Job Number": 1,
        "Repository": "repo",
        "Retry Count": 1,
        "Run Time": 1.1,
        "Skipped": 0,
        "Skipped Rate": 0.0,
        "Status": "failed",
        "Success": 0,
        "Success Rate": 0.0,
        "Test Suite": "suite",
        "Timestamp": "2024-01-01T00:00:00Z",
        "Total": 1,
        "Workflow": "main",
    },
    {
        "Date": "2024-01-02",
        "Execution Time": 1.2,
        "Failure": 0,
        "Failure Rate": 0.0,
        "Fixme": 1,
        "Fixme Rate": 100.0,
        "Job Number": 2,
        "Repository": "repo",
        "Retry Count": 0,
        "Run Time": 1.2,
        "Skipped": 1,
        "Skipped Rate": 100.0,
        "Status": "success",
        "Success": 0,
        "Success Rate": 0.0,
        "Test Suite": "suite",
        "Timestamp": "2024-01-02T00:00:00Z",
        "Total": 1,
        "Workflow": "main",
    },
    {
        "Date": "2024-01-03",
        "Execution Time": 1.3,
        "Failure": 0,
        "Failure Rate": 0.0,
        "Fixme": 0,
        "Fixme Rate": 0.0,
        "Job Number": 3,
        "Repository": "repo",
        "Retry Count": 1,
        "Run Time": 1.3,
        "Skipped": 0,
        "Skipped Rate": 0.0,
        "Status": "success",
        "Success": 1,
        "Success Rate": 100.0,
        "Test Suite": "suite",
        "Timestamp": "2024-01-03T00:00:00Z",
        "Total": 1,
        "Workflow": "main",
    },
    {
        "Date": "2024-01-04",
        "Execution Time": 1.4,
        "Failure": 0,
        "Failure Rate": 0.0,
        "Fixme": 0,
        "Fixme Rate": 0.0,
        "Job Number": 4,
        "Repository": "repo",
        "Retry Count": 0,
        "Run Time": 1.4,
        "Skipped": 1,
        "Skipped Rate": 100.0,
        "Status": "success",
        "Success": 0,
        "Success Rate": 0.0,
        "Test Suite": "suite",
        "Timestamp": "2024-01-04T00:00:00Z",
        "Total": 1,
        "Workflow": "main",
    },
    {
        "Date": "2024-01-05",
        "Execution Time": 1.5,
        "Failure": 0,
        "Failure Rate": 0.0,
        "Fixme": 0,
        "Fixme Rate": 0.0,
        "Job Number": 5,
        "Repository": "repo",
        "Retry Count": 0,
        "Run Time": 1.5,
        "Skipped": 0,
        "Skipped Rate": 0.0,
        "Status": "success",
        "Success": 1,
        "Success Rate": 100.0,
        "Test Suite": "suite",
        "Timestamp": "2024-01-05T00:00:00Z",
        "Total": 1,
        "Workflow": "main",
    },
]

LLVM_COV_SAMPLE_DIRECTORY = "llvm_cov_json_samples"
LLVM_COV_REPORT_LIST: list[CoverageJson] = [
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
        repository=REPOSITORY,
        workflow=WORKFLOW,
        test_suite=TEST_SUITE,
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
LLVM_COV_JSON: list[dict[str, Any]] = [
    {
        "Branch Count": 0,
        "Branch Covered": 0,
        "Branch Not Covered": 0,
        "Branch Percent": 0.0,
        "Date": "2024-08-30",
        "Function Count": 1007,
        "Function Covered": 589,
        "Function Not Covered": 418,
        "Function Percent": 58.490566037735846,
        "Job Number": 1,
        "Line Count": 9441,
        "Line Covered": 5761,
        "Line Excluded": None,
        "Line Not Covered": 3680,
        "Line Percent": 61.0210782756064,
        "Repository": "repo",
        "Test Suite": "suite",
        "Timestamp": "2024-08-30T19:56:50Z",
        "Workflow": "main",
    }
]

PYTEST_SAMPLE_DIRECTORY = "pytest_json_samples"
PYTEST_REPORT_LIST: list[CoverageJson] = [
    PytestReport(
        job_number=1,
        job_timestamp="2024-08-29T17:43:41Z",
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
        repository=REPOSITORY,
        workflow=WORKFLOW,
        test_suite=TEST_SUITE,
        date="2024-08-29",
        timestamp="2024-08-29T17:43:41Z",
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
PYTEST_JSON: list[dict[str, Any]] = [
    {
        "Branch Count": 943,
        "Branch Covered": 737,
        "Branch Not Covered": 206,
        "Branch Percent": 78.15482502651113,
        "Date": "2024-08-29",
        "Function Count": None,
        "Function Covered": None,
        "Function Not Covered": None,
        "Function Percent": None,
        "Job Number": 1,
        "Line Count": 3782,
        "Line Covered": 3138,
        "Line Excluded": 217,
        "Line Not Covered": 644,
        "Line Percent": 82.01058201058201,
        "Repository": "repo",
        "Test Suite": "suite",
        "Timestamp": "2024-08-29T17:43:41Z",
        "Workflow": "main",
    }
]


class ConfigValues(BaseModel):
    """Grouping common config sample data."""

    project_id: str
    dataset_name: str


class SampleCoverageData(BaseModel):
    """Grouping of test coverage sample data."""

    sample_directory: Path
    coverage_json_group: CoverageJsonGroup
    report_results: list[CoverageReporterResult]
    json_rows: list[dict[str, Any]]

    @property
    def sample_files(self) -> list[str]:
        """Test files in sample directory"""
        return [file_path.name for file_path in self.sample_directory.iterdir()]


class SampleResultsData(BaseModel):
    """Grouping of test result sample data."""

    artifact_group: JUnitXmlGroup
    report_results: list[SuiteReporterResult]
    json_rows: list[dict[str, Any]]


@pytest.fixture
def config() -> ConfigValues:
    """Provide the base path to the test data directory."""
    return ConfigValues(
        project_id="project",
        dataset_name="dataset",
    )


@pytest.fixture
def test_data_directory() -> Path:
    """Provide the base path to the test data directory."""
    return Path(__file__).parent / "test_data"


@pytest.fixture
def coverage_llvm_cov_data(test_data_directory: Path) -> SampleCoverageData:
    """Provide the llvm-cov coverage report sample data."""
    return SampleCoverageData(
        sample_directory=test_data_directory / LLVM_COV_SAMPLE_DIRECTORY,
        coverage_json_group=CoverageJsonGroup(
            repository=REPOSITORY,
            workflow=WORKFLOW,
            test_suite=TEST_SUITE,
            coverage_jsons=LLVM_COV_REPORT_LIST,
        ),
        report_results=LLVM_COV_REPORT_RESULTS,
        json_rows=LLVM_COV_JSON,
    )


@pytest.fixture
def coverage_pytest_data(test_data_directory: Path) -> SampleCoverageData:
    """Provide the pytest coverage report sample data."""
    return SampleCoverageData(
        sample_directory=test_data_directory / PYTEST_SAMPLE_DIRECTORY,
        coverage_json_group=CoverageJsonGroup(
            repository=REPOSITORY,
            workflow=WORKFLOW,
            test_suite=TEST_SUITE,
            coverage_jsons=PYTEST_REPORT_LIST,
        ),
        report_results=PYTEST_REPORT_RESULTS,
        json_rows=PYTEST_JSON,
    )


@pytest.fixture
def results_artifact_data(test_data_directory: Path) -> SampleResultsData:
    """Provide the artifact only test suite report sample data."""
    return SampleResultsData(
        artifact_group=JUnitXmlGroup(
            repository=REPOSITORY,
            workflow=WORKFLOW,
            test_suite=TEST_SUITE,
            junit_xmls=JUNIT_XML_JOB_TEST_SUITES_LIST,
        ),
        report_results=ARTIFACT_RESULTS,
        json_rows=ARTIFACT_JSON,
    )
