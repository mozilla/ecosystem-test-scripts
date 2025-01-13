# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""Tests for the CoverageReporter module."""

import logging
from typing import Any

import pytest
from pytest import LogCaptureFixture
from pytest_mock import MockerFixture

from scripts.metric_reporter.parser.coverage_json_parser import LlvmCovReport, PytestReport
from scripts.metric_reporter.reporter.coverage_reporter import (
    CoverageReporter,
    CoverageReporterResult,
)
from tests.metric_reporter.conftest import ConfigValues, SampleCoverageData


@pytest.mark.parametrize(
    "fixture", ["coverage_llvm_cov_data", "coverage_pytest_data"], ids=["llvm-cov", "pytest"]
)
def test_coverage_reporter_init(
    config: ConfigValues, fixture: str, request: pytest.FixtureRequest
) -> None:
    """Test CoverageReporter initialization with llvm-cov and pytest report data.

    Args:
        config (ConfigValues): pytest fixture for common config values.
        fixture (str): The name of the fixture with coverage sample data.
        request (FixtureRequest): A pytest request object for accessing fixtures.
    """
    coverage_data: SampleCoverageData = request.getfixturevalue(fixture)
    expected_results: list[CoverageReporterResult] = coverage_data.report_results

    reporter = CoverageReporter(
        config.repository, config.workflow, config.test_suite, coverage_data.report_list
    )

    assert reporter.results == expected_results


@pytest.mark.parametrize(
    "fixture, last_update_return_value",
    [
        ("coverage_llvm_cov_data", []),
        ("coverage_llvm_cov_data", [{"last_update": "2024-01-01T00:00:00Z"}]),
        ("coverage_pytest_data", []),
        ("coverage_pytest_data", [{"last_update": "2024-01-01T00:00:00Z"}]),
    ],
    ids=[
        "llvm-cov_new_table",
        "llvm-cov_existing_table",
        "pytest_new_table",
        "pytest_existing_table",
    ],
)
def test_coverage_reporter_update_table_with_new_results(
    mocker: MockerFixture,
    config: ConfigValues,
    fixture: str,
    request: pytest.FixtureRequest,
    last_update_return_value: list[dict[str, str]],
) -> None:
    """Test CoverageReporter update_table method with new coverage results.

    Args:
        mocker (MockerFixture): pytest_mock fixture for mocking.
        config (ConfigValues): pytest fixture for common config values.
        fixture (str): The name of the fixture with coverage sample data.
        request (FixtureRequest): A pytest request object for accessing fixtures.
        last_update_return_value (list[dict[str, str]]): Value returned by get_last_update mock.
    """
    coverage_data: SampleCoverageData = request.getfixturevalue(fixture)

    get_last_update_query_mock = mocker.MagicMock()
    get_last_update_query_mock.result.return_value = last_update_return_value
    check_rows_exist_query_mock = mocker.MagicMock()
    check_rows_exist_query_mock.result.return_value = []
    client_mock = mocker.MagicMock()
    client_mock.query.side_effect = [get_last_update_query_mock, check_rows_exist_query_mock]
    client_mock.insert_rows_json.return_value = []

    expected_table_id = f"{config.project_id}.{config.dataset_name}.{config.repository}_coverage"
    expected_results: list[dict[str, Any]] = coverage_data.json_rows

    reporter = CoverageReporter(
        config.repository, config.workflow, config.test_suite, coverage_data.report_list
    )

    reporter.update_table(client_mock, config.project_id, config.dataset_name)

    client_mock.insert_rows_json.assert_called_once_with(expected_table_id, expected_results)


@pytest.mark.parametrize(
    "fixture", ["coverage_llvm_cov_data", "coverage_pytest_data"], ids=["llvm-cov", "pytest"]
)
def test_coverage_reporter_update_table_with_new_results_and_row_duplication(
    caplog: LogCaptureFixture,
    mocker: MockerFixture,
    config: ConfigValues,
    fixture: str,
    request: pytest.FixtureRequest,
) -> None:
    """Test CoverageReporter update_table method with new results, but a duplicate is found before
       insertion.

    Args:
        caplog (LogCaptureFixture): pytest fixture for capturing log output.
        mocker (MockerFixture): pytest_mock fixture for mocking.
        config (ConfigValues): pytest fixture for common config values.
        fixture (str): The name of the fixture with coverage sample data.
        request (FixtureRequest): A pytest request object for accessing fixtures.
    """
    coverage_data: SampleCoverageData = request.getfixturevalue(fixture)

    get_last_update_query_mock = mocker.MagicMock()
    get_last_update_query_mock.result.return_value = [{"last_update": "2024-01-01T00:00:00Z"}]
    check_rows_exist_query_mock = mocker.MagicMock()
    check_rows_exist_query_mock.result.return_value = [{"1": 1}]
    client_mock = mocker.MagicMock()
    client_mock.query.side_effect = [get_last_update_query_mock, check_rows_exist_query_mock]

    expected_log = (
        f"Detected one or more results from "
        f"{config.repository}/{config.workflow}/{config.test_suite} already exist in table "
        f"{config.project_id}.{config.dataset_name}.{config.repository}_coverage. Aborting insert."
    )

    reporter = CoverageReporter(
        config.repository, config.workflow, config.test_suite, coverage_data.report_list
    )

    with caplog.at_level(logging.WARNING):
        reporter.update_table(client_mock, config.project_id, config.dataset_name)

        assert expected_log in caplog.text


@pytest.mark.parametrize(
    "fixture", ["coverage_llvm_cov_data", "coverage_pytest_data"], ids=["llvm-cov", "pytest"]
)
def test_coverage_reporter_update_table_without_new_results(
    caplog: LogCaptureFixture,
    mocker: MockerFixture,
    config: ConfigValues,
    fixture: str,
    request: pytest.FixtureRequest,
) -> None:
    """Test CoverageReporter update_table method with old results.

    Args:
        caplog (LogCaptureFixture): pytest fixture for capturing log output.
        mocker (MockerFixture): pytest_mock fixture for mocking.
        config (ConfigValues): pytest fixture for common config values.
        fixture (str): The name of the fixture with coverage sample data.
        request (FixtureRequest): A pytest request object for accessing fixtures.
    """
    coverage_data: SampleCoverageData = request.getfixturevalue(fixture)

    get_last_update_query_mock = mocker.MagicMock()
    get_last_update_query_mock.result.return_value = [{"last_update": "2024-09-01T00:00:00Z"}]
    mock_client = mocker.MagicMock()
    mock_client.query.return_value = get_last_update_query_mock

    expected_log = (
        f"There are no new results for {config.repository}/{config.workflow}/{config.test_suite} "
        f"to add to {config.project_id}.{config.dataset_name}.{config.repository}_coverage."
    )

    reporter = CoverageReporter(
        config.repository, config.workflow, config.test_suite, coverage_data.report_list
    )

    with caplog.at_level(logging.INFO):
        reporter.update_table(mock_client, config.project_id, config.dataset_name)

        assert expected_log in caplog.text


def test_coverage_reporter_update_table_with_empty_test_results(
    caplog: LogCaptureFixture, mocker: MockerFixture, config: ConfigValues
) -> None:
    """Test CoverageReporter update_table method with no test results.

    Args:
        caplog (LogCaptureFixture): pytest fixture for capturing log output.
        mocker (MockerFixture): pytest_mock fixture for mocking.
        config (ConfigValues): pytest fixture for common config values.
    """
    coverage_artifact_list: list[LlvmCovReport | PytestReport] = []

    client_mock = mocker.MagicMock()

    expected_log = (
        f"There are no results for {config.repository}/{config.workflow}/{config.test_suite} "
        f"to add to {config.project_id}.{config.dataset_name}.{config.repository}_coverage."
    )

    reporter = CoverageReporter(
        config.repository, config.workflow, config.test_suite, coverage_artifact_list
    )

    with caplog.at_level(logging.INFO):
        reporter.update_table(client_mock, config.project_id, config.dataset_name)

        assert client_mock.mock_calls == [], "Expected no interactions with the mock client."
        assert expected_log in caplog.text
