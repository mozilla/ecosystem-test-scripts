# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""Module for test configurations for the Metric Reporter."""

from pathlib import Path
from typing import Any

import pytest
from pydantic import BaseModel

from scripts.metric_reporter.parser.circleci_json_parser import (
    CircleCIJob,
    CircleCIJobTestMetadata,
    CircleCITestMetadata,
)
from scripts.metric_reporter.parser.coverage_json_parser import (
    PytestReport,
    PytestMeta,
    PytestTotals,
    LlvmCovDataItem,
    LlvmCovReport,
    LlvmCovStats,
    LlvmCovTotals,
)
from scripts.metric_reporter.parser.junit_xml_parser import (
    JUnitXmlFailure,
    JUnitXmlJobTestSuites,
    JUnitXmlProperty,
    JUnitXmlSkipped,
    JUnitXmlSystemOut,
    JUnitXmlTestCase,
    JUnitXmlTestSuite,
    JUnitXmlTestSuites,
)
from scripts.metric_reporter.reporter.coverage_reporter import CoverageReporterResult
from scripts.metric_reporter.reporter.suite_reporter import SuiteReporterResult

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

ARTIFACT_RESULTS: list[SuiteReporterResult] = [
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
ARTIFACT_CSV: str = (
    "Repository,Workflow,Test Suite,Date,Timestamp,Job Number,Status,Execution Time,Job Time,Run Time,Success,Failure,Skipped,Fixme,Unknown,Retry Count,Total,Success Rate,Failure Rate,Skipped Rate,Fixme Rate,Unknown Rate\r\n"
    "repo,main,suite,2024-01-01,2024-01-01T00:00:00Z,1,failed,1.1,,1.1,0,1,0,0,0,1,1,0.0,100.0,0.0,0.0,0.0\r\n"
    "repo,main,suite,2024-01-02,2024-01-02T00:00:00Z,2,success,1.2,,1.2,0,0,1,1,0,0,1,0.0,0.0,100.0,100.0,0.0\r\n"
    "repo,main,suite,2024-01-03,2024-01-03T00:00:00Z,3,success,1.3,,1.3,1,0,0,0,0,1,1,100.0,0.0,0.0,0.0,0.0\r\n"
    "repo,main,suite,2024-01-04,2024-01-04T00:00:00Z,4,success,1.4,,1.4,0,0,1,0,0,0,1,0.0,0.0,100.0,0.0,0.0\r\n"
    "repo,main,suite,2024-01-05,2024-01-05T00:00:00Z,5,success,1.5,,1.5,1,0,0,0,0,0,1,100.0,0.0,0.0,0.0,0.0\r\n"
)
ARTIFACT_JSON: list[dict[str, Any]] = [
    {
        "Date": "2024-01-01",
        "Execution Time": 1.1,
        "Failure": 1,
        "Failure Rate": 100.0,
        "Fixme": 0,
        "Fixme Rate": 0.0,
        "Job Number": 1,
        "Job Time": None,
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
        "Unknown": 0,
        "Unknown Rate": 0.0,
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
        "Job Time": None,
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
        "Unknown": 0,
        "Unknown Rate": 0.0,
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
        "Job Time": None,
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
        "Unknown": 0,
        "Unknown Rate": 0.0,
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
        "Job Time": None,
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
        "Unknown": 0,
        "Unknown Rate": 0.0,
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
        "Job Time": None,
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
        "Unknown": 0,
        "Unknown Rate": 0.0,
        "Workflow": "main",
    },
]

METADATA_RESULTS: list[SuiteReporterResult] = [
    SuiteReporterResult(
        repository="repo",
        workflow="main",
        test_suite="suite",
        timestamp="2024-01-01T00:00:00Z",
        date="2024-01-01",
        job=1,
        run_time=1.1,
        job_time=3600.0,
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
        job_time=3600.0,
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
        job_time=3600.0,
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
        job_time=3600.0,
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
        job_time=3600.0,
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
        job_time=3600.0,
        unknown=1,
    ),
]
METADATA_CSV: str = (
    "Repository,Workflow,Test Suite,Date,Timestamp,Job Number,Status,Execution Time,Job Time,Run Time,Success,Failure,Skipped,Fixme,Unknown,Retry Count,Total,Success Rate,Failure Rate,Skipped Rate,Fixme Rate,Unknown Rate\r\n"
    "repo,main,suite,2024-01-01,2024-01-01T00:00:00Z,1,failed,,3600.0,1.1,0,1,0,0,0,0,1,0.0,100.0,0.0,0.0,0.0\r\n"
    "repo,main,suite,2024-01-02,2024-01-02T00:00:00Z,2,success,,3600.0,1.2,0,0,1,0,0,0,1,0.0,0.0,100.0,0.0,0.0\r\n"
    "repo,main,suite,2024-01-03,2024-01-03T00:00:00Z,3,success,,3600.0,1.3,1,0,0,0,0,0,1,100.0,0.0,0.0,0.0,0.0\r\n"
    "repo,main,suite,2024-01-04,2024-01-04T00:00:00Z,4,success,,3600.0,1.4,0,0,1,0,0,0,1,0.0,0.0,100.0,0.0,0.0\r\n"
    "repo,main,suite,2024-01-05,2024-01-05T00:00:00Z,5,success,,3600.0,1.5,1,0,0,0,0,0,1,100.0,0.0,0.0,0.0,0.0\r\n"
    "repo,main,suite,2024-01-06,2024-01-06T00:00:00Z,6,unknown,,3600.0,1.6,0,0,0,0,1,0,1,0.0,0.0,0.0,0.0,100.0\r\n"
)
METADATA_JSON: list[dict[str, Any]] = [
    {
        "Date": "2024-01-01",
        "Execution Time": None,
        "Failure": 1,
        "Failure Rate": 100.0,
        "Fixme": 0,
        "Fixme Rate": 0.0,
        "Job Number": 1,
        "Job Time": 3600.0,
        "Repository": "repo",
        "Retry Count": 0,
        "Run Time": 1.1,
        "Skipped": 0,
        "Skipped Rate": 0.0,
        "Status": "failed",
        "Success": 0,
        "Success Rate": 0.0,
        "Test Suite": "suite",
        "Timestamp": "2024-01-01T00:00:00Z",
        "Total": 1,
        "Unknown": 0,
        "Unknown Rate": 0.0,
        "Workflow": "main",
    },
    {
        "Date": "2024-01-02",
        "Execution Time": None,
        "Failure": 0,
        "Failure Rate": 0.0,
        "Fixme": 0,
        "Fixme Rate": 0.0,
        "Job Number": 2,
        "Job Time": 3600.0,
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
        "Unknown": 0,
        "Unknown Rate": 0.0,
        "Workflow": "main",
    },
    {
        "Date": "2024-01-03",
        "Execution Time": None,
        "Failure": 0,
        "Failure Rate": 0.0,
        "Fixme": 0,
        "Fixme Rate": 0.0,
        "Job Number": 3,
        "Job Time": 3600.0,
        "Repository": "repo",
        "Retry Count": 0,
        "Run Time": 1.3,
        "Skipped": 0,
        "Skipped Rate": 0.0,
        "Status": "success",
        "Success": 1,
        "Success Rate": 100.0,
        "Test Suite": "suite",
        "Timestamp": "2024-01-03T00:00:00Z",
        "Total": 1,
        "Unknown": 0,
        "Unknown Rate": 0.0,
        "Workflow": "main",
    },
    {
        "Date": "2024-01-04",
        "Execution Time": None,
        "Failure": 0,
        "Failure Rate": 0.0,
        "Fixme": 0,
        "Fixme Rate": 0.0,
        "Job Number": 4,
        "Job Time": 3600.0,
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
        "Unknown": 0,
        "Unknown Rate": 0.0,
        "Workflow": "main",
    },
    {
        "Date": "2024-01-05",
        "Execution Time": None,
        "Failure": 0,
        "Failure Rate": 0.0,
        "Fixme": 0,
        "Fixme Rate": 0.0,
        "Job Number": 5,
        "Job Time": 3600.0,
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
        "Unknown": 0,
        "Unknown Rate": 0.0,
        "Workflow": "main",
    },
    {
        "Date": "2024-01-06",
        "Execution Time": None,
        "Failure": 0,
        "Failure Rate": 0.0,
        "Fixme": 0,
        "Fixme Rate": 0.0,
        "Job Number": 6,
        "Job Time": 3600.0,
        "Repository": "repo",
        "Retry Count": 0,
        "Run Time": 1.6,
        "Skipped": 0,
        "Skipped Rate": 0.0,
        "Status": "unknown",
        "Success": 0,
        "Success Rate": 0.0,
        "Test Suite": "suite",
        "Timestamp": "2024-01-06T00:00:00Z",
        "Total": 1,
        "Unknown": 1,
        "Unknown Rate": 100.0,
        "Workflow": "main",
    },
]

ARTIFACT_AND_METADATA_RESULTS: list[SuiteReporterResult] = [
    SuiteReporterResult(
        repository="repo",
        workflow="main",
        test_suite="suite",
        timestamp="2024-01-01T00:00:00Z",
        date="2024-01-01",
        job=1,
        run_time=1.1,
        execution_time=1.1,
        job_time=3600.0,
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
        job_time=3600.0,
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
        job_time=3600.0,
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
        job_time=3600.0,
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
        job_time=3600.0,
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
        job_time=3600.0,
        unknown=1,
    ),
]
ARTIFACT_AND_METADATA_CSV: str = (
    "Repository,Workflow,Test Suite,Date,Timestamp,Job Number,Status,Execution Time,Job Time,Run Time,Success,Failure,Skipped,Fixme,Unknown,Retry Count,Total,Success Rate,Failure Rate,Skipped Rate,Fixme Rate,Unknown Rate\r\n"
    "repo,main,suite,2024-01-01,2024-01-01T00:00:00Z,1,failed,1.1,3600.0,1.1,0,1,0,0,0,1,1,0.0,100.0,0.0,0.0,0.0\r\n"
    "repo,main,suite,2024-01-02,2024-01-02T00:00:00Z,2,success,1.2,3600.0,1.2,0,0,1,1,0,0,1,0.0,0.0,100.0,100.0,0.0\r\n"
    "repo,main,suite,2024-01-03,2024-01-03T00:00:00Z,3,success,1.3,3600.0,1.3,1,0,0,0,0,1,1,100.0,0.0,0.0,0.0,0.0\r\n"
    "repo,main,suite,2024-01-04,2024-01-04T00:00:00Z,4,success,1.4,3600.0,1.4,0,0,1,0,0,0,1,0.0,0.0,100.0,0.0,0.0\r\n"
    "repo,main,suite,2024-01-05,2024-01-05T00:00:00Z,5,success,1.5,3600.0,1.5,1,0,0,0,0,0,1,100.0,0.0,0.0,0.0,0.0\r\n"
    "repo,main,suite,2024-01-06,2024-01-06T00:00:00Z,6,unknown,,3600.0,1.6,0,0,0,0,1,0,1,0.0,0.0,0.0,0.0,100.0\r\n"
)
ARTIFACT_AND_METADATA_JSON: list[dict[str, Any]] = [
    {
        "Repository": "repo",
        "Workflow": "main",
        "Test Suite": "suite",
        "Date": "2024-01-01",
        "Timestamp": "2024-01-01T00:00:00Z",
        "Job Number": 1,
        "Status": "failed",
        "Execution Time": 1.1,
        "Job Time": 3600.0,
        "Run Time": 1.1,
        "Success": 0,
        "Failure": 1,
        "Skipped": 0,
        "Fixme": 0,
        "Unknown": 0,
        "Retry Count": 1,
        "Total": 1,
        "Success Rate": 0.0,
        "Failure Rate": 100.0,
        "Skipped Rate": 0.0,
        "Fixme Rate": 0.0,
        "Unknown Rate": 0.0,
    },
    {
        "Repository": "repo",
        "Workflow": "main",
        "Test Suite": "suite",
        "Date": "2024-01-02",
        "Timestamp": "2024-01-02T00:00:00Z",
        "Job Number": 2,
        "Status": "success",
        "Execution Time": 1.2,
        "Job Time": 3600.0,
        "Run Time": 1.2,
        "Success": 0,
        "Failure": 0,
        "Skipped": 1,
        "Fixme": 1,
        "Unknown": 0,
        "Retry Count": 0,
        "Total": 1,
        "Success Rate": 0.0,
        "Failure Rate": 0.0,
        "Skipped Rate": 100.0,
        "Fixme Rate": 100.0,
        "Unknown Rate": 0.0,
    },
    {
        "Repository": "repo",
        "Workflow": "main",
        "Test Suite": "suite",
        "Date": "2024-01-03",
        "Timestamp": "2024-01-03T00:00:00Z",
        "Job Number": 3,
        "Status": "success",
        "Execution Time": 1.3,
        "Job Time": 3600.0,
        "Run Time": 1.3,
        "Success": 1,
        "Failure": 0,
        "Skipped": 0,
        "Fixme": 0,
        "Unknown": 0,
        "Retry Count": 1,
        "Total": 1,
        "Success Rate": 100.0,
        "Failure Rate": 0.0,
        "Skipped Rate": 0.0,
        "Fixme Rate": 0.0,
        "Unknown Rate": 0.0,
    },
    {
        "Repository": "repo",
        "Workflow": "main",
        "Test Suite": "suite",
        "Date": "2024-01-04",
        "Timestamp": "2024-01-04T00:00:00Z",
        "Job Number": 4,
        "Status": "success",
        "Execution Time": 1.4,
        "Job Time": 3600.0,
        "Run Time": 1.4,
        "Success": 0,
        "Failure": 0,
        "Skipped": 1,
        "Fixme": 0,
        "Unknown": 0,
        "Retry Count": 0,
        "Total": 1,
        "Success Rate": 0.0,
        "Failure Rate": 0.0,
        "Skipped Rate": 100.0,
        "Fixme Rate": 0.0,
        "Unknown Rate": 0.0,
    },
    {
        "Repository": "repo",
        "Workflow": "main",
        "Test Suite": "suite",
        "Date": "2024-01-05",
        "Timestamp": "2024-01-05T00:00:00Z",
        "Job Number": 5,
        "Status": "success",
        "Execution Time": 1.5,
        "Job Time": 3600.0,
        "Run Time": 1.5,
        "Success": 1,
        "Failure": 0,
        "Skipped": 0,
        "Fixme": 0,
        "Unknown": 0,
        "Retry Count": 0,
        "Total": 1,
        "Success Rate": 100.0,
        "Failure Rate": 0.0,
        "Skipped Rate": 0.0,
        "Fixme Rate": 0.0,
        "Unknown Rate": 0.0,
    },
    {
        "Repository": "repo",
        "Workflow": "main",
        "Test Suite": "suite",
        "Date": "2024-01-06",
        "Timestamp": "2024-01-06T00:00:00Z",
        "Job Number": 6,
        "Status": "unknown",
        "Execution Time": None,
        "Job Time": 3600.0,
        "Run Time": 1.6,
        "Success": 0,
        "Failure": 0,
        "Skipped": 0,
        "Fixme": 0,
        "Unknown": 1,
        "Retry Count": 0,
        "Total": 1,
        "Success Rate": 0.0,
        "Failure Rate": 0.0,
        "Skipped Rate": 0.0,
        "Fixme Rate": 0.0,
        "Unknown Rate": 100.0,
    },
]


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
PYTEST_CSV: str = (
    "Repository,Workflow,Test Suite,Date,Timestamp,Job Number,Line Count,Line Covered,Line Not Covered,Line Excluded,Line Percent,Function Count,Function Covered,Function Not Covered,Function Percent,Branch Count,Branch Covered,Branch Not Covered,Branch Percent\r\n"
    "repo,main,suite,2024-08-29,2024-08-29T17:43:41Z,1,3782,3138,644,217,82.01058201058201,,,,,943,737,206,78.15482502651113\r\n"
)
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

    repository: str
    workflow: str
    test_suite: str
    project_id: str
    dataset_name: str


class SampleCoverageData(BaseModel):
    """Grouping of test coverage sample data."""

    sample_directory: Path
    report_list: list[LlvmCovReport | PytestReport]
    report_results: list[CoverageReporterResult]
    csv: str
    json_rows: list[dict[str, Any]]


class SampleResultsData(BaseModel):
    """Grouping of test result sample data."""

    metadata_list: list[CircleCIJobTestMetadata] | None
    artifact_list: list[JUnitXmlJobTestSuites] | None
    report_results: list[SuiteReporterResult]
    csv: str
    json_rows: list[dict[str, Any]]


@pytest.fixture
def config() -> ConfigValues:
    """Provide the base path to the test data directory."""
    return ConfigValues(
        repository="repo",
        workflow="main",
        test_suite="suite",
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
        report_list=LLVM_COV_REPORT_LIST,
        report_results=LLVM_COV_REPORT_RESULTS,
        csv=LLVM_COV_CSV,
        json_rows=LLVM_COV_JSON,
    )


@pytest.fixture
def coverage_pytest_data(test_data_directory: Path) -> SampleCoverageData:
    """Provide the pytest coverage report sample data."""
    return SampleCoverageData(
        sample_directory=test_data_directory / PYTEST_SAMPLE_DIRECTORY,
        report_list=PYTEST_REPORT_LIST,
        report_results=PYTEST_REPORT_RESULTS,
        csv=PYTEST_CSV,
        json_rows=PYTEST_JSON,
    )


@pytest.fixture
def results_artifact_data(test_data_directory: Path) -> SampleResultsData:
    """Provide the artifact only test suite report sample data."""
    return SampleResultsData(
        metadata_list=None,
        artifact_list=JUNIT_XML_JOB_TEST_SUITES_LIST,
        report_results=ARTIFACT_RESULTS,
        csv=ARTIFACT_CSV,
        json_rows=ARTIFACT_JSON,
    )


@pytest.fixture
def results_metadata_data(test_data_directory: Path) -> SampleResultsData:
    """Provide the metadata only test suite report sample data."""
    return SampleResultsData(
        metadata_list=CIRCLECI_JOB_TEST_METADATA_LIST,
        artifact_list=None,
        report_results=METADATA_RESULTS,
        csv=METADATA_CSV,
        json_rows=METADATA_JSON,
    )


@pytest.fixture
def results_artifact_and_metadata_data(test_data_directory: Path) -> SampleResultsData:
    """Provide the artifact and metadata test suite report sample data."""
    return SampleResultsData(
        metadata_list=CIRCLECI_JOB_TEST_METADATA_LIST,
        artifact_list=JUNIT_XML_JOB_TEST_SUITES_LIST,
        report_results=ARTIFACT_AND_METADATA_RESULTS,
        csv=ARTIFACT_AND_METADATA_CSV,
        json_rows=ARTIFACT_AND_METADATA_JSON,
    )
