# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""Tests for the AveragesReporter module."""

import logging
from pathlib import Path
from typing import Sequence
from unittest.mock import MagicMock

from pytest import LogCaptureFixture
from pytest_mock import MockerFixture

from scripts.metric_reporter.averages_reporter import AveragesReporter, AveragesReporterResult
from scripts.metric_reporter.suite_reporter import SuiteReporterResult

SUITE_RESULTS: Sequence[SuiteReporterResult] = [
    SuiteReporterResult(
        repository="repo",
        workflow="main",
        test_suite="suite",
        timestamp="2024-01-01T00:00:00Z",
        date="2024-01-01",
        job=1,
        run_time=0,
        execution_time=None,
        job_time=None,
    ),
    SuiteReporterResult(
        repository="repo",
        workflow="main",
        test_suite="suite",
        timestamp="2024-01-30T00:00:00Z",
        date="2024-01-31",
        job=2,
        run_time=15,
        execution_time=None,
        job_time=25,
    ),
    SuiteReporterResult(
        repository="repo",
        workflow="main",
        test_suite="suite",
        timestamp="2024-03-01T00:00:00Z",
        date="2024-03-01",
        job=3,
        run_time=10,
        execution_time=15,
        job_time=20,
    ),
    SuiteReporterResult(
        repository="repo",
        workflow="main",
        test_suite="suite",
        timestamp="2024-03-31T00:00:00Z",
        date="2024-03-31",
        job=4,
        run_time=15,
        execution_time=20,
        job_time=25,
    ),
    SuiteReporterResult(
        repository="repo",
        workflow="main",
        test_suite="suite",
        timestamp="2024-04-30T00:00:00Z",
        date="2024-04-30",
        job=5,
        run_time=10,
        execution_time=15,
        job_time=20,
    ),
]

# This list only contains boundary values
EXPECTED_RESULTS = [
    AveragesReporterResult(
        repository="repo",
        workflow="main",
        test_suite="suite",
        start_date_30="2024-01-01",
        stop_date_30="2024-01-31",
        suite_count_30=2,
        success_rate_30=100.0,
        run_time_30=7.5,
        job_time_30=12.5,
        execution_time_30=None,
        start_date_60="2023-12-02",
        stop_date_60="2024-01-31",
        suite_count_60=2,
        success_rate_60=100.0,
        run_time_60=7.5,
        job_time_60=12.5,
        execution_time_60=None,
        start_date_90="2023-11-02",
        stop_date_90="2024-01-31",
        suite_count_90=2,
        success_rate_90=100.0,
        run_time_90=7.5,
        job_time_90=12.5,
        execution_time_90=None,
    ),
    AveragesReporterResult(
        repository="repo",
        workflow="main",
        test_suite="suite",
        start_date_30="2024-01-02",
        stop_date_30="2024-02-01",
        suite_count_30=1,
        success_rate_30=100.0,
        run_time_30=15.0,
        job_time_30=25.0,
        execution_time_30=None,
        start_date_60="2023-12-03",
        stop_date_60="2024-02-01",
        suite_count_60=2,
        success_rate_60=100.0,
        run_time_60=7.5,
        job_time_60=12.5,
        execution_time_60=None,
        start_date_90="2023-11-03",
        stop_date_90="2024-02-01",
        suite_count_90=2,
        success_rate_90=100.0,
        run_time_90=7.5,
        job_time_90=12.5,
        execution_time_90=None,
    ),
    AveragesReporterResult(
        repository="repo",
        workflow="main",
        test_suite="suite",
        start_date_30="2024-01-30",
        stop_date_30="2024-02-29",
        suite_count_30=1,
        success_rate_30=100.0,
        run_time_30=15.0,
        job_time_30=25.0,
        execution_time_30=None,
        start_date_60="2023-12-31",
        stop_date_60="2024-02-29",
        suite_count_60=2,
        success_rate_60=100.0,
        run_time_60=7.5,
        job_time_60=12.5,
        execution_time_60=None,
        start_date_90="2023-12-01",
        stop_date_90="2024-02-29",
        suite_count_90=2,
        success_rate_90=100.0,
        run_time_90=7.5,
        job_time_90=12.5,
        execution_time_90=None,
    ),
    AveragesReporterResult(
        repository="repo",
        workflow="main",
        test_suite="suite",
        start_date_30="2024-01-31",
        stop_date_30="2024-03-01",
        suite_count_30=2,
        success_rate_30=100.0,
        run_time_30=12.5,
        job_time_30=22.5,
        execution_time_30=7.5,
        start_date_60="2024-01-01",
        stop_date_60="2024-03-01",
        suite_count_60=3,
        success_rate_60=100.0,
        run_time_60=8.333333333333334,
        job_time_60=15.0,
        execution_time_60=5.0,
        start_date_90="2023-12-02",
        stop_date_90="2024-03-01",
        suite_count_90=3,
        success_rate_90=100.0,
        run_time_90=8.333333333333334,
        job_time_90=15.0,
        execution_time_90=5.0,
    ),
    AveragesReporterResult(
        repository="repo",
        workflow="main",
        test_suite="suite",
        start_date_30="2024-02-01",
        stop_date_30="2024-03-02",
        suite_count_30=1,
        success_rate_30=100.0,
        run_time_30=10.0,
        job_time_30=20.0,
        execution_time_30=15.0,
        start_date_60="2024-01-02",
        stop_date_60="2024-03-02",
        suite_count_60=2,
        success_rate_60=100.0,
        run_time_60=12.5,
        job_time_60=22.5,
        execution_time_60=7.5,
        start_date_90="2023-12-03",
        stop_date_90="2024-03-02",
        suite_count_90=3,
        success_rate_90=100.0,
        run_time_90=8.333333333333334,
        job_time_90=15.0,
        execution_time_90=5.0,
    ),
    AveragesReporterResult(
        repository="repo",
        workflow="main",
        test_suite="suite",
        start_date_30="2024-02-29",
        stop_date_30="2024-03-30",
        suite_count_30=1,
        success_rate_30=100.0,
        run_time_30=10.0,
        job_time_30=20.0,
        execution_time_30=15.0,
        start_date_60="2024-01-30",
        stop_date_60="2024-03-30",
        suite_count_60=2,
        success_rate_60=100.0,
        run_time_60=12.5,
        job_time_60=22.5,
        execution_time_60=7.5,
        start_date_90="2023-12-31",
        stop_date_90="2024-03-30",
        suite_count_90=3,
        success_rate_90=100.0,
        run_time_90=8.333333333333334,
        job_time_90=15.0,
        execution_time_90=5.0,
    ),
    AveragesReporterResult(
        repository="repo",
        workflow="main",
        test_suite="suite",
        start_date_30="2024-03-01",
        stop_date_30="2024-03-31",
        suite_count_30=2,
        success_rate_30=100.0,
        run_time_30=12.5,
        job_time_30=22.5,
        execution_time_30=17.5,
        start_date_60="2024-01-31",
        stop_date_60="2024-03-31",
        suite_count_60=3,
        success_rate_60=100.0,
        run_time_60=13.333333333333334,
        job_time_60=23.333333333333332,
        execution_time_60=11.666666666666666,
        start_date_90="2024-01-01",
        stop_date_90="2024-03-31",
        suite_count_90=4,
        success_rate_90=100.0,
        run_time_90=10.0,
        job_time_90=17.5,
        execution_time_90=8.75,
    ),
    AveragesReporterResult(
        repository="repo",
        workflow="main",
        test_suite="suite",
        start_date_30="2024-03-02",
        stop_date_30="2024-04-01",
        suite_count_30=1,
        success_rate_30=100.0,
        run_time_30=15.0,
        job_time_30=25.0,
        execution_time_30=20.0,
        start_date_60="2024-02-01",
        stop_date_60="2024-04-01",
        suite_count_60=2,
        success_rate_60=100.0,
        run_time_60=12.5,
        job_time_60=22.5,
        execution_time_60=17.5,
        start_date_90="2024-01-02",
        stop_date_90="2024-04-01",
        suite_count_90=3,
        success_rate_90=100.0,
        run_time_90=13.333333333333334,
        job_time_90=23.333333333333332,
        execution_time_90=11.666666666666666,
    ),
    AveragesReporterResult(
        repository="repo",
        workflow="main",
        test_suite="suite",
        start_date_30="2024-03-30",
        stop_date_30="2024-04-29",
        suite_count_30=1,
        success_rate_30=100.0,
        run_time_30=15.0,
        job_time_30=25.0,
        execution_time_30=20.0,
        start_date_60="2024-02-29",
        stop_date_60="2024-04-29",
        suite_count_60=2,
        success_rate_60=100.0,
        run_time_60=12.5,
        job_time_60=22.5,
        execution_time_60=17.5,
        start_date_90="2024-01-30",
        stop_date_90="2024-04-29",
        suite_count_90=3,
        success_rate_90=100.0,
        run_time_90=13.333333333333334,
        job_time_90=23.333333333333332,
        execution_time_90=11.666666666666666,
    ),
    AveragesReporterResult(
        repository="repo",
        workflow="main",
        test_suite="suite",
        start_date_30="2024-03-31",
        stop_date_30="2024-04-30",
        suite_count_30=2,
        success_rate_30=100.0,
        run_time_30=12.5,
        job_time_30=22.5,
        execution_time_30=17.5,
        start_date_60="2024-03-01",
        stop_date_60="2024-04-30",
        suite_count_60=3,
        success_rate_60=100.0,
        run_time_60=11.666666666666666,
        job_time_60=21.666666666666668,
        execution_time_60=16.666666666666668,
        start_date_90="2024-01-31",
        stop_date_90="2024-04-30",
        suite_count_90=4,
        success_rate_90=100.0,
        run_time_90=12.5,
        job_time_90=22.5,
        execution_time_90=12.5,
    ),
]


def test_averages_reporter_init(test_data_directory: Path) -> None:
    """Test AveragesReporter initialization."""
    repository = "repo"
    workflow = "main"
    test_suite = "suite"

    reporter = AveragesReporter(repository, workflow, test_suite, SUITE_RESULTS)

    # Testing the boundaries which occur on the 1st, 30th, 60th, 90th and 120th day marks
    assert (
        len(reporter.results) == 91
        and reporter.results[0] == EXPECTED_RESULTS[0]
        and reporter.results[1] == EXPECTED_RESULTS[1]
        and reporter.results[29] == EXPECTED_RESULTS[2]
        and reporter.results[30] == EXPECTED_RESULTS[3]
        and reporter.results[31] == EXPECTED_RESULTS[4]
        and reporter.results[59] == EXPECTED_RESULTS[5]
        and reporter.results[60] == EXPECTED_RESULTS[6]
        and reporter.results[61] == EXPECTED_RESULTS[7]
        and reporter.results[89] == EXPECTED_RESULTS[8]
        and reporter.results[90] == EXPECTED_RESULTS[9]
    )


def test_averages_reporter_output_csv(test_data_directory: Path, mocker: MockerFixture) -> None:
    """Test AveragesReporter output_results_csv method with test results.

    Args:
        test_data_directory (Path): Test data directory for the Metric Reporter.
        mocker (MockerFixture): pytest_mock fixture for mocking.
    """
    repository = "repo"
    workflow = "main"
    test_suite = "suite"
    expected_csv_path: Path = test_data_directory / "averages_csv" / "averages.csv"
    with expected_csv_path.open("r", newline="") as file:
        expected_csv = file.read()
    reporter = AveragesReporter(repository, workflow, test_suite, SUITE_RESULTS)
    report_path: Path = test_data_directory / "fake_path.csv"

    mock_open: MagicMock = mocker.mock_open()
    mocker.patch("builtins.open", mock_open)
    mocker.patch("os.makedirs")

    reporter.output_csv(report_path)

    mock_open.assert_called_once_with(report_path, "w", newline="")
    handle = mock_open()
    actual_csv = "".join(call[0][0] for call in handle.write.call_args_list)
    assert actual_csv == expected_csv


def test_averages_reporter_output_csv_with_empty_test_results(
    test_data_directory: Path, caplog: LogCaptureFixture, mocker: MockerFixture
) -> None:
    """Test AveragesReporter output_results_csv method with no test results.

    Args:
        test_data_directory (Path): Test data directory for the Metric Reporter.
        caplog (LogCaptureFixture): pytest fixture for capturing log output.
        mocker (MockerFixture): pytest_mock fixture for mocking.
    """
    repository = "repo"
    workflow = "main"
    test_suite = "suite"
    suite_results: Sequence[SuiteReporterResult] = []
    reporter = AveragesReporter(repository, workflow, test_suite, suite_results)
    report_path = test_data_directory / "fake_path.csv"
    expected_log = f"No data to write to {report_path}."

    with caplog.at_level(logging.INFO):
        mock_open: MagicMock = mocker.mock_open()
        mocker.patch("builtins.open", mock_open)
        mocker.patch("os.makedirs")

        reporter.output_csv(report_path)

        mock_open.assert_not_called()
        assert expected_log in caplog.text
