# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""Tests for the SuiteReporter module."""

import logging

import pytest
from pytest import LogCaptureFixture
from pytest_mock import MockerFixture

from scripts.metric_reporter.parser.junit_xml_parser import JUnitXmlJobTestSuites
from scripts.metric_reporter.reporter.suite_reporter import SuiteReporter
from tests.metric_reporter.conftest import ConfigValues, SampleResultsData


def test_suite_reporter_init(
    config: ConfigValues, results_artifact_data: SampleResultsData
) -> None:
    """Test SuiteReporter initialization.

    Args:
        config (ConfigValues): pytest fixture for common config values.
        results_artifact_data (SampleResultsData): results artifact data.
    """
    reporter = SuiteReporter(
        config.repository, config.workflow, config.test_suite, results_artifact_data.artifact_list
    )

    assert reporter.results == results_artifact_data.report_results


@pytest.mark.parametrize(
    "last_update_return_value",
    [[], [{"last_update": "2023-01-01T00:00:00Z"}]],
    ids=["new_table", "existing_table"],
)
def test_suite_reporter_update_table_with_new_results(
    mocker: MockerFixture,
    config: ConfigValues,
    results_artifact_data: SampleResultsData,
    last_update_return_value: list[dict[str, str]],
) -> None:
    """Test SuiteReporter update_table method with new test results.

    Args:
        mocker (MockerFixture): pytest_mock fixture for mocking.
        config (ConfigValues): pytest fixture for common config values.
        results_artifact_data (SampleResultsData): results artifact data.
        last_update_return_value (list[dict[str, str]]): Value returned by get_last_update mock
    """
    get_last_update_query_mock = mocker.MagicMock()
    get_last_update_query_mock.result.return_value = last_update_return_value
    check_rows_exist_query_mock = mocker.MagicMock()
    check_rows_exist_query_mock.result.return_value = []
    client_mock = mocker.MagicMock()
    client_mock.query.side_effect = [get_last_update_query_mock, check_rows_exist_query_mock]
    client_mock.insert_rows_json.return_value = []

    expected_table_id = (
        f"{config.project_id}.{config.dataset_name}.{config.repository}_suite_results"
    )

    reporter = SuiteReporter(
        config.repository, config.workflow, config.test_suite, results_artifact_data.artifact_list
    )

    reporter.update_table(client_mock, config.project_id, config.dataset_name)

    client_mock.insert_rows_json.assert_called_once_with(
        expected_table_id, results_artifact_data.json_rows
    )


def test_suite_reporter_update_table_with_new_results_and_row_duplication(
    caplog: LogCaptureFixture,
    mocker: MockerFixture,
    config: ConfigValues,
    results_artifact_data: SampleResultsData,
) -> None:
    """Test SuiteReporter update_table method with new test results, but a duplicate is found before
       insertion.

    Args:
        caplog (LogCaptureFixture): pytest fixture for capturing log output.
        mocker (MockerFixture): pytest_mock fixture for mocking.
        config (ConfigValues): pytest fixture for common config values.
        results_artifact_data (SampleResultsData): artifact data.
    """
    get_last_update_query_mock = mocker.MagicMock()
    get_last_update_query_mock.result.return_value = [{"last_update": "2024-01-01T00:00:00Z"}]
    check_rows_exist_query_mock = mocker.MagicMock()
    check_rows_exist_query_mock.result.return_value = [{"1": 1}]
    client_mock = mocker.MagicMock()
    client_mock.query.side_effect = [get_last_update_query_mock, check_rows_exist_query_mock]

    expected_log = (
        f"Detected one or more results from "
        f"{config.repository}/{config.workflow}/{config.test_suite} already exist in table "
        f"{config.project_id}.{config.dataset_name}.{config.repository}_suite_results. Aborting insert."
    )

    reporter = SuiteReporter(
        config.repository, config.workflow, config.test_suite, results_artifact_data.artifact_list
    )

    with caplog.at_level(logging.WARNING):
        reporter.update_table(client_mock, config.project_id, config.dataset_name)

        assert expected_log in caplog.text


def test_suite_reporter_update_table_without_new_test_results(
    caplog: LogCaptureFixture,
    mocker: MockerFixture,
    config: ConfigValues,
    results_artifact_data: SampleResultsData,
) -> None:
    """Test SuiteReporter update_table method with old test results.

    Args:
        caplog (LogCaptureFixture): pytest fixture for capturing log output.
        mocker (MockerFixture): pytest_mock fixture for mocking.
        config (ConfigValues): pytest fixture for common config values.
        results_artifact_data (SampleResultsData): artifact data.
    """
    get_last_update_query_mock = mocker.MagicMock()
    get_last_update_query_mock.result.return_value = [{"last_update": "2024-01-06T00:00:00Z"}]
    mock_client = mocker.MagicMock()
    mock_client.query.return_value = get_last_update_query_mock

    expected_log = (
        f"There are no new results for {config.repository}/{config.workflow}/{config.test_suite} "
        f"to add to {config.project_id}.{config.dataset_name}.{config.repository}_suite_results."
    )

    reporter = SuiteReporter(
        config.repository, config.workflow, config.test_suite, results_artifact_data.artifact_list
    )

    with caplog.at_level(logging.INFO):
        reporter.update_table(mock_client, config.project_id, config.dataset_name)

        assert expected_log in caplog.text


def test_suite_reporter_update_table_with_empty_test_results(
    caplog: LogCaptureFixture, mocker: MockerFixture, config: ConfigValues
) -> None:
    """Test SuiteReporter update_table method with no test results.

    Args:
        caplog (LogCaptureFixture): pytest fixture for capturing log output.
        mocker (MockerFixture): pytest_mock fixture for mocking.
        config (ConfigValues): pytest fixture for common config values.
    """
    artifact_list: list[JUnitXmlJobTestSuites] | None = None

    client_mock = mocker.MagicMock()

    expected_log = (
        f"There are no results for {config.repository}/{config.workflow}/{config.test_suite} to "
        f"add to {config.project_id}.{config.dataset_name}.{config.repository}_suite_results."
    )

    reporter = SuiteReporter(config.repository, config.workflow, config.test_suite, artifact_list)

    with caplog.at_level(logging.INFO):
        reporter.update_table(client_mock, config.project_id, config.dataset_name)

        assert client_mock.mock_calls == [], "Expected no interactions with the mock client."
        assert expected_log in caplog.text
