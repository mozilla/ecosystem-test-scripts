# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""Tests for the AveragesReporter module."""

import logging
from datetime import date
from pathlib import Path
from typing import Sequence

from pytest import LogCaptureFixture
from pytest_mock import MockerFixture

from scripts.metric_reporter.reporter.averages_reporter import (
    AveragesReporter,
    AveragesReporterResult,
)
from scripts.metric_reporter.reporter.suite_reporter import SuiteReporterResult
from tests.metric_reporter.conftest import ConfigValues

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

EXPECTED_JSON = [
    {
        "End Date 30": "2024-04-30",
        "End Date 60": "2024-04-30",
        "End Date 90": "2024-04-30",
        "Execution Time 30": 17.5,
        "Execution Time 60": 16.666666666666668,
        "Execution Time 90": 12.5,
        "Job Time 30": 22.5,
        "Job Time 60": 21.666666666666668,
        "Job Time 90": 22.5,
        "Repository": "repo",
        "Run Time 30": 12.5,
        "Run Time 60": 11.666666666666666,
        "Run Time 90": 12.5,
        "Start Date 30": "2024-03-31",
        "Start Date 60": "2024-03-01",
        "Start Date 90": "2024-01-31",
        "Success Rate 30": 100.0,
        "Success Rate 60": 100.0,
        "Success Rate 90": 100.0,
        "Suite Count 30": 2,
        "Suite Count 60": 3,
        "Suite Count 90": 4,
        "Test Suite": "suite",
        "Workflow": "main",
    }
]


def test_averages_reporter_init(config: ConfigValues, test_data_directory: Path) -> None:
    """Test AveragesReporter initialization.

    Args:
        config (ConfigValues): pytest fixture for common config values.
        test_data_directory (Path): Test data directory for the Metric Reporter.
    """
    reporter = AveragesReporter(
        config.repository, config.workflow, config.test_suite, SUITE_RESULTS
    )

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


def test_averages_reporter_update_table_with_new_results(
    mocker: MockerFixture, config: ConfigValues
) -> None:
    """Test AveragesReporter update_table method with new coverage results.

    Args:
        mocker (MockerFixture): pytest_mock fixture for mocking.
        config (ConfigValues): pytest fixture for common config values.
    """
    get_last_update_query_mock = mocker.MagicMock()
    get_last_update_query_mock.result.return_value = [{"last_update": date(2024, 4, 29)}]
    check_rows_exist_query_mock = mocker.MagicMock()
    check_rows_exist_query_mock.result.return_value = []
    client_mock = mocker.MagicMock()
    client_mock.query.side_effect = [get_last_update_query_mock, check_rows_exist_query_mock]
    client_mock.insert_rows_json.return_value = []

    expected_table_id = f"{config.project_id}.{config.dataset_name}.{config.repository}_averages"

    reporter = AveragesReporter(
        config.repository, config.workflow, config.test_suite, SUITE_RESULTS
    )

    reporter.update_table(client_mock, config.project_id, config.dataset_name)

    client_mock.insert_rows_json.assert_called_once_with(expected_table_id, EXPECTED_JSON)


def test_averages_reporter_update_table_with_new_results_and_row_duplication(
    caplog: LogCaptureFixture, mocker: MockerFixture, config: ConfigValues
) -> None:
    """Test AveragesReporter update_table method with new results, but a duplicate is found before
       insertion.

    Args:
        caplog (LogCaptureFixture): pytest fixture for capturing log output.
        mocker (MockerFixture): pytest_mock fixture for mocking.
        config (ConfigValues): pytest fixture for common config values.
    """
    get_last_update_query_mock = mocker.MagicMock()
    get_last_update_query_mock.result.return_value = [{"last_update": date(2024, 1, 1)}]
    check_rows_exist_query_mock = mocker.MagicMock()
    check_rows_exist_query_mock.result.return_value = [{"1": 1}]
    client_mock = mocker.MagicMock()
    client_mock.query.side_effect = [get_last_update_query_mock, check_rows_exist_query_mock]

    expected_log = (
        f"Detected one or more results from "
        f"{config.repository}/{config.workflow}/{config.test_suite} already exist in table "
        f"{config.project_id}.{config.dataset_name}.{config.repository}_averages. Aborting insert."
    )

    reporter = AveragesReporter(
        config.repository, config.workflow, config.test_suite, SUITE_RESULTS
    )

    with caplog.at_level(logging.WARNING):
        reporter.update_table(client_mock, config.project_id, config.dataset_name)

        assert expected_log in caplog.text


def test_averages_reporter_update_table_without_new_results(
    caplog: LogCaptureFixture, mocker: MockerFixture, config: ConfigValues
) -> None:
    """Test AveragesReporter update_table method with old results.

    Args:
        caplog (LogCaptureFixture): pytest fixture for capturing log output.
        mocker (MockerFixture): pytest_mock fixture for mocking.
        config (ConfigValues): pytest fixture for common config values.
    """
    get_last_update_query_mock = mocker.MagicMock()
    get_last_update_query_mock.result.return_value = [{"last_update": date(2024, 5, 1)}]
    mock_client = mocker.MagicMock()
    mock_client.query.return_value = get_last_update_query_mock

    expected_log = (
        f"There are no new averages for {config.repository}/{config.workflow}/{config.test_suite} "
        f"to add to {config.project_id}.{config.dataset_name}.{config.repository}_averages."
    )

    reporter = AveragesReporter(
        config.repository, config.workflow, config.test_suite, SUITE_RESULTS
    )

    with caplog.at_level(logging.INFO):
        reporter.update_table(mock_client, config.project_id, config.dataset_name)

        assert expected_log in caplog.text


def test_averages_reporter_update_table_with_empty_test_results(
    caplog: LogCaptureFixture, mocker: MockerFixture, config: ConfigValues
) -> None:
    """Test AveragesReporter update_table method with no test results.

    Args:
        caplog (LogCaptureFixture): pytest fixture for capturing log output.
        mocker (MockerFixture): pytest_mock fixture for mocking.
        config (ConfigValues): pytest fixture for common config values.
    """
    client_mock = mocker.MagicMock()

    expected_log = (
        f"There are no averages for {config.repository}/{config.workflow}/{config.test_suite} "
        f"to add to {config.project_id}.{config.dataset_name}.{config.repository}_averages."
    )

    reporter = AveragesReporter(config.repository, config.workflow, config.test_suite, [])

    with caplog.at_level(logging.INFO):
        reporter.update_table(client_mock, config.project_id, config.dataset_name)

        assert client_mock.mock_calls == [], "Expected no interactions with the mock client."
        assert expected_log in caplog.text
