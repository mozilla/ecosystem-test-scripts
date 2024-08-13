# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""Tests for the SuiteReporter module."""

import logging
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from pytest import LogCaptureFixture
from pytest_mock import MockerFixture

from scripts.metric_reporter.circleci_json_parser import (
    CircleCIJobTestMetadata,
    CircleCITestMetadata,
    CircleCIJob,
)
from scripts.metric_reporter.junit_xml_parser import (
    JUnitXmlFailure,
    JUnitXmlJobTestSuites,
    JUnitXmlProperty,
    JUnitXmlSkipped,
    JUnitXmlSystemOut,
    JUnitXmlTestCase,
    JUnitXmlTestSuite,
    JUnitXmlTestSuites,
)
from scripts.metric_reporter.suite_reporter import SuiteReporter, SuiteReporterResult

CIRCLECI_JOB_TEST_METADATA_LIST: list[CircleCIJobTestMetadata] | None = [
    CircleCIJobTestMetadata(
        job=CircleCIJob(
            dependencies=[],
            job_number=1,
            id="1",
            started_at="2024-01-01T00:00:00Z",
            name="test-job",
            project_slug="test/test-project",
            status="failed",
            type="build",
            stopped_at="2024-01-01T01:00:00Z",
        ),
        test_metadata=[
            CircleCITestMetadata(
                classname="test_class",
                name="test_failure",
                result="failure",
                message="",
                run_time=1.1,
                source="test_source",
            )
        ],
    ),
    CircleCIJobTestMetadata(
        job=CircleCIJob(
            dependencies=[],
            job_number=2,
            id="2",
            started_at="2024-01-02T00:00:00Z",
            name="test-job",
            project_slug="test/test-project",
            status="success",
            type="build",
            stopped_at="2024-01-02T01:00:00Z",
        ),
        test_metadata=[
            CircleCITestMetadata(
                classname="test_class",
                name="test_fixme",
                result="skipped",
                message="",
                run_time=1.2,
                source="test_source",
            )
        ],
    ),
    CircleCIJobTestMetadata(
        job=CircleCIJob(
            dependencies=[],
            job_number=3,
            id="3",
            started_at="2024-01-03T00:00:00Z",
            name="test-job",
            project_slug="test/test-project",
            status="success",
            type="build",
            stopped_at="2024-01-03T01:00:00Z",
        ),
        test_metadata=[
            CircleCITestMetadata(
                classname="test_class",
                name="test_retry",
                result="system-out",
                message="",
                run_time=1.3,
                source="test_source",
            )
        ],
    ),
    CircleCIJobTestMetadata(
        job=CircleCIJob(
            dependencies=[],
            job_number=4,
            id="4",
            started_at="2024-01-04T00:00:00Z",
            name="test-job",
            project_slug="test/test-project",
            status="success",
            type="build",
            stopped_at="2024-01-04T01:00:00Z",
        ),
        test_metadata=[
            CircleCITestMetadata(
                classname="test_class",
                name="test_skipped",
                result="skipped",
                message="",
                run_time=1.4,
                source="test_source",
            )
        ],
    ),
    CircleCIJobTestMetadata(
        job=CircleCIJob(
            dependencies=[],
            job_number=5,
            id="5",
            started_at="2024-01-05T00:00:00Z",
            name="test-job",
            project_slug="test/test-project",
            status="success",
            type="build",
            stopped_at="2024-01-05T01:00:00Z",
        ),
        test_metadata=[
            CircleCITestMetadata(
                classname="test_class",
                name="test_success",
                result="success",
                message="",
                run_time=1.5,
                source="test_source",
            )
        ],
    ),
    CircleCIJobTestMetadata(
        job=CircleCIJob(
            dependencies=[],
            job_number=6,
            id="6",
            started_at="2024-01-06T00:00:00Z",
            name="test-job",
            project_slug="test/test-project",
            status="success",
            type="build",
            stopped_at="2024-01-06T01:00:00Z",
        ),
        test_metadata=[
            CircleCITestMetadata(
                classname="test_class",
                name="test_unknown",
                result="system-err",
                message="",
                run_time=1.6,
                source="test_source",
            )
        ],
    ),
]

JUNIT_XML_JOB_TEST_SUITES_LIST: list[JUnitXmlJobTestSuites] | None = [
    JUnitXmlJobTestSuites(
        job=1,
        test_suites=[
            JUnitXmlTestSuites(
                id="",
                name="",
                tests=1,
                failures=1,
                skipped=0,
                errors=0,
                time=1.1,
                timestamp=None,
                test_suites=[
                    JUnitXmlTestSuite(
                        name="test_class",
                        timestamp="2024-01-01T00:00:00Z",
                        hostname="local",
                        tests=1,
                        failures=1,
                        skipped=0,
                        time=1.1,
                        errors=0,
                        test_cases=[
                            JUnitXmlTestCase(
                                name="test_failure",
                                classname="test_class",
                                time=1.1,
                                properties=None,
                                skipped=None,
                                failure=JUnitXmlFailure(
                                    message="test_class:1:1 test_failure",
                                    type="FAILURE",
                                    text="\n                Error Msg\n            ",
                                ),
                                system_out=JUnitXmlSystemOut(
                                    text=(
                                        "[[ATTACHMENT|../test_class/test_failure/trace.zip]]"
                                        "[[ATTACHMENT|../test_class/test_failure-retry1/trace.zip]]"
                                    )
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
        test_suites=[
            JUnitXmlTestSuites(
                id="",
                name="",
                tests=1,
                failures=0,
                skipped=1,
                errors=0,
                time=1.2,
                timestamp=None,
                test_suites=[
                    JUnitXmlTestSuite(
                        name="test_class",
                        timestamp="2024-01-02T00:00:00Z",
                        hostname="local",
                        tests=1,
                        failures=0,
                        skipped=1,
                        time=1.2,
                        errors=0,
                        test_cases=[
                            JUnitXmlTestCase(
                                name="test_fixme",
                                classname="test_class",
                                time=1.2,
                                properties=[JUnitXmlProperty(name="fixme", value="see JIRA-0000")],
                                skipped=JUnitXmlSkipped(reason=None),
                                failure=None,
                                system_out=None,
                            )
                        ],
                    )
                ],
            )
        ],
    ),
    JUnitXmlJobTestSuites(
        job=3,
        test_suites=[
            JUnitXmlTestSuites(
                id="",
                name="",
                tests=1,
                failures=0,
                skipped=0,
                errors=0,
                time=1.3,
                timestamp=None,
                test_suites=[
                    JUnitXmlTestSuite(
                        name="test_class",
                        timestamp="2024-01-03T00:00:00Z",
                        hostname="local",
                        tests=1,
                        failures=0,
                        skipped=0,
                        time=1.3,
                        errors=0,
                        test_cases=[
                            JUnitXmlTestCase(
                                name="test_retry",
                                classname="test_class",
                                time=1.3,
                                properties=None,
                                skipped=None,
                                failure=None,
                                system_out=JUnitXmlSystemOut(
                                    text="[[ATTACHMENT|../test_class/test_retry/trace.zip]]"
                                ),
                            )
                        ],
                    )
                ],
            )
        ],
    ),
    JUnitXmlJobTestSuites(
        job=4,
        test_suites=[
            JUnitXmlTestSuites(
                id=None,
                name="",
                tests=1,
                failures=0,
                skipped=None,
                errors=0,
                time=1.4,
                timestamp=None,
                test_suites=[
                    JUnitXmlTestSuite(
                        name="test_class",
                        timestamp="2024-01-04T00:00:00Z",
                        hostname=None,
                        tests=1,
                        failures=0,
                        skipped=1,
                        time=1.4,
                        errors=0,
                        test_cases=[
                            JUnitXmlTestCase(
                                name="test_class",
                                classname="test_skipped",
                                time=1.4,
                                properties=None,
                                skipped=JUnitXmlSkipped(reason=None),
                                failure=None,
                                system_out=None,
                            )
                        ],
                    )
                ],
            )
        ],
    ),
    JUnitXmlJobTestSuites(
        job=5,
        test_suites=[
            JUnitXmlTestSuites(
                id=None,
                name=None,
                tests=None,
                failures=None,
                skipped=None,
                errors=None,
                time=None,
                timestamp=None,
                test_suites=[
                    JUnitXmlTestSuite(
                        name="test_class",
                        timestamp="2024-01-05T00:00:00Z",
                        hostname="ip-10-0-175-52",
                        tests=1,
                        failures=0,
                        skipped=0,
                        time=1.5,
                        errors=0,
                        test_cases=[
                            JUnitXmlTestCase(
                                name="test_class",
                                classname="test_success",
                                time=1.5,
                                properties=None,
                                skipped=None,
                                failure=None,
                                system_out=None,
                            )
                        ],
                    )
                ],
            )
        ],
    ),
]

EXPECTED_ARTIFACT_RESULTS: list[SuiteReporterResult] = [
    SuiteReporterResult(
        repository="repo",
        workflow="main",
        test_suite="suite",
        timestamp="2024-01-01T00:00:00Z",
        date="2024-01-01",
        job=1,
        run_time=1.1,
        execution_time=1.1,
        failure=1,
        retry=1,
    ),
    SuiteReporterResult(
        repository="repo",
        workflow="main",
        test_suite="suite",
        timestamp="2024-01-02T00:00:00Z",
        date="2024-01-02",
        job=2,
        run_time=1.2,
        execution_time=1.2,
        skipped=1,
        fixme=1,
    ),
    SuiteReporterResult(
        repository="repo",
        workflow="main",
        test_suite="suite",
        timestamp="2024-01-03T00:00:00Z",
        date="2024-01-03",
        job=3,
        run_time=1.3,
        execution_time=1.3,
        success=1,
        retry=1,
    ),
    SuiteReporterResult(
        repository="repo",
        workflow="main",
        test_suite="suite",
        timestamp="2024-01-04T00:00:00Z",
        date="2024-01-04",
        job=4,
        run_time=1.4,
        execution_time=1.4,
        skipped=1,
    ),
    SuiteReporterResult(
        repository="repo",
        workflow="main",
        test_suite="suite",
        timestamp="2024-01-05T00:00:00Z",
        date="2024-01-05",
        job=5,
        run_time=1.5,
        execution_time=1.5,
        success=1,
    ),
]

EXPECTED_METADATA_RESULTS: list[SuiteReporterResult] = [
    SuiteReporterResult(
        repository="repo",
        workflow="main",
        test_suite="suite",
        timestamp="2024-01-01T00:00:00Z",
        date="2024-01-01",
        job=1,
        run_time=1.1,
        job_execution_time=3600.0,
        failure=1,
    ),
    SuiteReporterResult(
        repository="repo",
        workflow="main",
        test_suite="suite",
        timestamp="2024-01-02T00:00:00Z",
        date="2024-01-02",
        job=2,
        run_time=1.2,
        job_execution_time=3600.0,
        skipped=1,
    ),
    SuiteReporterResult(
        repository="repo",
        workflow="main",
        test_suite="suite",
        timestamp="2024-01-03T00:00:00Z",
        date="2024-01-03",
        job=3,
        run_time=1.3,
        job_execution_time=3600.0,
        success=1,
    ),
    SuiteReporterResult(
        repository="repo",
        workflow="main",
        test_suite="suite",
        timestamp="2024-01-04T00:00:00Z",
        date="2024-01-04",
        job=4,
        run_time=1.4,
        job_execution_time=3600.0,
        skipped=1,
    ),
    SuiteReporterResult(
        repository="repo",
        workflow="main",
        test_suite="suite",
        timestamp="2024-01-05T00:00:00Z",
        date="2024-01-05",
        job=5,
        run_time=1.5,
        job_execution_time=3600.0,
        success=1,
    ),
    SuiteReporterResult(
        repository="repo",
        workflow="main",
        test_suite="suite",
        timestamp="2024-01-06T00:00:00Z",
        date="2024-01-06",
        job=6,
        run_time=1.6,
        job_execution_time=3600.0,
        unknown=1,
    ),
]

EXPECTED_ARTIFACT_AND_METADATA_RESULTS: list[SuiteReporterResult] = [
    SuiteReporterResult(
        repository="repo",
        workflow="main",
        test_suite="suite",
        timestamp="2024-01-01T00:00:00Z",
        date="2024-01-01",
        job=1,
        run_time=1.1,
        execution_time=1.1,
        job_execution_time=3600.0,
        failure=1,
        retry=1,
    ),
    SuiteReporterResult(
        repository="repo",
        workflow="main",
        test_suite="suite",
        timestamp="2024-01-02T00:00:00Z",
        date="2024-01-02",
        job=2,
        run_time=1.2,
        execution_time=1.2,
        job_execution_time=3600.0,
        skipped=1,
        fixme=1,
    ),
    SuiteReporterResult(
        repository="repo",
        workflow="main",
        test_suite="suite",
        timestamp="2024-01-03T00:00:00Z",
        date="2024-01-03",
        job=3,
        run_time=1.3,
        execution_time=1.3,
        job_execution_time=3600.0,
        success=1,
        retry=1,
    ),
    SuiteReporterResult(
        repository="repo",
        workflow="main",
        test_suite="suite",
        timestamp="2024-01-04T00:00:00Z",
        date="2024-01-04",
        job=4,
        run_time=1.4,
        execution_time=1.4,
        job_execution_time=3600.0,
        skipped=1,
    ),
    SuiteReporterResult(
        repository="repo",
        workflow="main",
        test_suite="suite",
        timestamp="2024-01-05T00:00:00Z",
        date="2024-01-05",
        job=5,
        run_time=1.5,
        execution_time=1.5,
        job_execution_time=3600.0,
        success=1,
    ),
    SuiteReporterResult(
        repository="repo",
        workflow="main",
        test_suite="suite",
        timestamp="2024-01-06T00:00:00Z",
        date="2024-01-06",
        job=6,
        run_time=1.6,
        job_execution_time=3600.0,
        unknown=1,
    ),
]

EXPECTED_ARTIFACT_CSV: str = (
    "Repository,Workflow,Test Suite,Date,Timestamp,Job Number,Status,Execution Time,Job Execution Time,Run Time,Success,Failure,Skipped,Fixme,Unknown,Retry Count,Total,Success Rate (%),Failure Rate (%),Skipped Rate (%),Fixme Rate (%),Unknown Rate (%)\r\n"
    "repo,main,suite,2024-01-01,2024-01-01T00:00:00Z,1,failed,1.1,,1.1,0,1,0,0,0,1,1,0.0,100.0,0.0,0.0,0.0\r\n"
    "repo,main,suite,2024-01-02,2024-01-02T00:00:00Z,2,success,1.2,,1.2,0,0,1,1,0,0,1,0.0,0.0,100.0,100.0,0.0\r\n"
    "repo,main,suite,2024-01-03,2024-01-03T00:00:00Z,3,success,1.3,,1.3,1,0,0,0,0,1,1,100.0,0.0,0.0,0.0,0.0\r\n"
    "repo,main,suite,2024-01-04,2024-01-04T00:00:00Z,4,success,1.4,,1.4,0,0,1,0,0,0,1,0.0,0.0,100.0,0.0,0.0\r\n"
    "repo,main,suite,2024-01-05,2024-01-05T00:00:00Z,5,success,1.5,,1.5,1,0,0,0,0,0,1,100.0,0.0,0.0,0.0,0.0\r\n"
)

EXPECTED_METADATA_CSV: str = (
    "Repository,Workflow,Test Suite,Date,Timestamp,Job Number,Status,Execution Time,Job Execution Time,Run Time,Success,Failure,Skipped,Fixme,Unknown,Retry Count,Total,Success Rate (%),Failure Rate (%),Skipped Rate (%),Fixme Rate (%),Unknown Rate (%)\r\n"
    "repo,main,suite,2024-01-01,2024-01-01T00:00:00Z,1,failed,,3600.0,1.1,0,1,0,0,0,0,1,0.0,100.0,0.0,0.0,0.0\r\n"
    "repo,main,suite,2024-01-02,2024-01-02T00:00:00Z,2,success,,3600.0,1.2,0,0,1,0,0,0,1,0.0,0.0,100.0,0.0,0.0\r\n"
    "repo,main,suite,2024-01-03,2024-01-03T00:00:00Z,3,success,,3600.0,1.3,1,0,0,0,0,0,1,100.0,0.0,0.0,0.0,0.0\r\n"
    "repo,main,suite,2024-01-04,2024-01-04T00:00:00Z,4,success,,3600.0,1.4,0,0,1,0,0,0,1,0.0,0.0,100.0,0.0,0.0\r\n"
    "repo,main,suite,2024-01-05,2024-01-05T00:00:00Z,5,success,,3600.0,1.5,1,0,0,0,0,0,1,100.0,0.0,0.0,0.0,0.0\r\n"
    "repo,main,suite,2024-01-06,2024-01-06T00:00:00Z,6,unknown,,3600.0,1.6,0,0,0,0,1,0,1,0.0,0.0,0.0,0.0,100.0\r\n"
)

EXPECTED_ARTIFACT_AND_METADATA_CSV: str = (
    "Repository,Workflow,Test Suite,Date,Timestamp,Job Number,Status,Execution Time,Job Execution Time,Run Time,Success,Failure,Skipped,Fixme,Unknown,Retry Count,Total,Success Rate (%),Failure Rate (%),Skipped Rate (%),Fixme Rate (%),Unknown Rate (%)\r\n"
    "repo,main,suite,2024-01-01,2024-01-01T00:00:00Z,1,failed,1.1,3600.0,1.1,0,1,0,0,0,1,1,0.0,100.0,0.0,0.0,0.0\r\n"
    "repo,main,suite,2024-01-02,2024-01-02T00:00:00Z,2,success,1.2,3600.0,1.2,0,0,1,1,0,0,1,0.0,0.0,100.0,100.0,0.0\r\n"
    "repo,main,suite,2024-01-03,2024-01-03T00:00:00Z,3,success,1.3,3600.0,1.3,1,0,0,0,0,1,1,100.0,0.0,0.0,0.0,0.0\r\n"
    "repo,main,suite,2024-01-04,2024-01-04T00:00:00Z,4,success,1.4,3600.0,1.4,0,0,1,0,0,0,1,0.0,0.0,100.0,0.0,0.0\r\n"
    "repo,main,suite,2024-01-05,2024-01-05T00:00:00Z,5,success,1.5,3600.0,1.5,1,0,0,0,0,0,1,100.0,0.0,0.0,0.0,0.0\r\n"
    "repo,main,suite,2024-01-06,2024-01-06T00:00:00Z,6,unknown,,3600.0,1.6,0,0,0,0,1,0,1,0.0,0.0,0.0,0.0,100.0\r\n"
)


@pytest.mark.parametrize(
    "metadata_list, artifact_list, expected_results",
    [
        (None, JUNIT_XML_JOB_TEST_SUITES_LIST, EXPECTED_ARTIFACT_RESULTS),
        (CIRCLECI_JOB_TEST_METADATA_LIST, None, EXPECTED_METADATA_RESULTS),
        (
            CIRCLECI_JOB_TEST_METADATA_LIST,
            JUNIT_XML_JOB_TEST_SUITES_LIST,
            EXPECTED_ARTIFACT_AND_METADATA_RESULTS,
        ),
    ],
    ids=[
        "with_artifact_test_results",
        "with_metadata_test_results",
        "with_artifact_metadata_test_results",
    ],
)
def test_suite_reporter_init(
    metadata_list: list[CircleCIJobTestMetadata] | None,
    artifact_list: list[JUnitXmlJobTestSuites] | None,
    expected_results: list[SuiteReporterResult],
) -> None:
    """Test SuiteReporter initialization.

    Args:
        metadata_list (list[CircleCIJobTestMetadata] | None): CircleCI Metadata.
        artifact_list (list[JUnitXmlJobTestSuites] | None): JUnit XML data.
        expected_results (list[SuiteReporterResult]): Expected results from the SuiteReporter.
    """
    repository = "repo"
    workflow = "main"
    test_suite = "suite"

    reporter = SuiteReporter(repository, workflow, test_suite, metadata_list, artifact_list)

    assert reporter.results == expected_results


@pytest.mark.parametrize(
    "metadata_list, artifact_list, expected_csv",
    [
        (None, JUNIT_XML_JOB_TEST_SUITES_LIST, EXPECTED_ARTIFACT_CSV),
        (CIRCLECI_JOB_TEST_METADATA_LIST, None, EXPECTED_METADATA_CSV),
        (
            CIRCLECI_JOB_TEST_METADATA_LIST,
            JUNIT_XML_JOB_TEST_SUITES_LIST,
            EXPECTED_ARTIFACT_AND_METADATA_CSV,
        ),
    ],
    ids=[
        "with_artifact_test_results",
        "with_metadata_test_results",
        "with_artifact_metadata_test_results",
    ],
)
def test_suite_reporter_output_csv(
    test_data_directory: Path,
    mocker: MockerFixture,
    metadata_list: list[CircleCIJobTestMetadata] | None,
    artifact_list: list[JUnitXmlJobTestSuites] | None,
    expected_csv: str,
) -> None:
    """Test SuiteReporter output_results_csv method with test results.

    Args:
        test_data_directory (Path): Test data directory for the Metric Reporter.
        mocker (MockerFixture): pytest_mock fixture for mocking.
        metadata_list (list[CircleCIJobTestMetadata] | None): CircleCI Metadata.
        artifact_list (list[JUnitXmlJobTestSuites] | None): JUnit XML data.
        expected_csv (dtr): Expected csv output from the SuiteReporter.
    """
    repository = "repo"
    workflow = "main"
    test_suite = "suite"
    reporter = SuiteReporter(repository, workflow, test_suite, metadata_list, artifact_list)
    report_path = test_data_directory / "fake_path.csv"

    mock_open: MagicMock = mocker.mock_open()
    mocker.patch("builtins.open", mock_open)
    mocker.patch("os.makedirs")

    reporter.output_results_csv(report_path)

    mock_open.assert_called_once_with(report_path, "w", newline="")
    handle = mock_open()
    actual_csv = "".join(call[0][0] for call in handle.write.call_args_list)
    assert actual_csv == expected_csv


def test_suite_reporter_output_csv_with_empty_test_results(
    test_data_directory: Path, caplog: LogCaptureFixture, mocker: MockerFixture
) -> None:
    """Test SuiteReporter output_results_csv method with no test results.

    Args:
        test_data_directory (Path): Test data directory for the Metric Reporter.
        caplog (LogCaptureFixture): pytest fixture for capturing log output.
        mocker (MockerFixture): pytest_mock fixture for mocking.
    """
    repository = "repo"
    workflow = "main"
    test_suite = "suite"
    metadata_list: list[CircleCIJobTestMetadata] | None = None
    artifact_list: list[JUnitXmlJobTestSuites] | None = None
    reporter = SuiteReporter(repository, workflow, test_suite, metadata_list, artifact_list)
    report_path = test_data_directory / "fake_path.csv"
    expected_log = "No data to write to the CSV file."

    with caplog.at_level(logging.INFO):
        mock_open: MagicMock = mocker.mock_open()
        mocker.patch("builtins.open", mock_open)
        mocker.patch("os.makedirs")

        reporter.output_results_csv(report_path)

        mock_open.assert_not_called()
        assert expected_log in caplog.text
