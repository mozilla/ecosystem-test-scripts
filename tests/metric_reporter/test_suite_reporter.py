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

from scripts.metric_reporter.parser.circleci_json_parser import CircleCIJobTestMetadata
from scripts.metric_reporter.parser.junit_xml_parser import JUnitXmlJobTestSuites
from scripts.metric_reporter.reporter.suite_reporter import SuiteReporter
from tests.metric_reporter.conftest import ConfigValues, SampleResultsData


@pytest.mark.parametrize(
    "fixture",
    ["results_artifact_data", "results_metadata_data", "results_artifact_and_metadata_data"],
    ids=["artifact_test_results", "metadata_test_results", "artifact_metadata_test_results"],
)
def test_suite_reporter_init(
    config: ConfigValues, fixture: str, request: pytest.FixtureRequest
) -> None:
    """Test SuiteReporter initialization.

    Args:
        config (ConfigValues): pytest fixture for common config values.
        fixture (str): The name of the fixture with coverage sample data.
        request (FixtureRequest): A pytest request object for accessing fixtures.
    """
    results_data: SampleResultsData = request.getfixturevalue(fixture)

    reporter = SuiteReporter(
        config.repository,
        config.workflow,
        config.test_suite,
        results_data.metadata_list,
        results_data.artifact_list,
    )

    assert reporter.results == results_data.report_results


@pytest.mark.parametrize(
    "fixture",
    ["results_artifact_data", "results_metadata_data", "results_artifact_and_metadata_data"],
    ids=["artifact_test_results", "metadata_test_results", "artifact_metadata_test_results"],
)
def test_suite_reporter_output_csv(
    mocker: MockerFixture,
    config: ConfigValues,
    test_data_directory: Path,
    fixture: str,
    request: pytest.FixtureRequest,
) -> None:
    """Test SuiteReporter output_csv method with test results.

    Args:
        mocker (MockerFixture): pytest_mock fixture for mocking.
        config (ConfigValues): pytest fixture for common config values.
        test_data_directory (Path): Test data directory for the Metric Reporter.
        fixture (str): The name of the fixture with coverage sample data.
        request (FixtureRequest): A pytest request object for accessing fixtures.
    """
    results_data: SampleResultsData = request.getfixturevalue(fixture)
    report_path = test_data_directory / "fake_path.csv"

    mock_open: MagicMock = mocker.mock_open()
    mocker.patch("builtins.open", mock_open)
    mocker.patch("os.makedirs")

    reporter = SuiteReporter(
        config.repository,
        config.workflow,
        config.test_suite,
        results_data.metadata_list,
        results_data.artifact_list,
    )

    reporter.output_csv(report_path)

    mock_open.assert_called_once_with(report_path, "w", newline="")
    handle = mock_open()
    actual_csv = "".join(call[0][0] for call in handle.write.call_args_list)
    assert actual_csv == results_data.csv


def test_suite_reporter_output_csv_with_empty_test_results(
    caplog: LogCaptureFixture,
    mocker: MockerFixture,
    config: ConfigValues,
    test_data_directory: Path,
) -> None:
    """Test SuiteReporter output_csv method with no test results.

    Args:
        caplog (LogCaptureFixture): pytest fixture for capturing log output.
        mocker (MockerFixture): pytest_mock fixture for mocking.
        config (ConfigValues): pytest fixture for common config values.
        test_data_directory (Path): Test data directory for the Metric Reporter.
    """
    metadata_list: list[CircleCIJobTestMetadata] | None = None
    artifact_list: list[JUnitXmlJobTestSuites] | None = None
    reporter = SuiteReporter(
        config.repository, config.workflow, config.test_suite, metadata_list, artifact_list
    )
    report_path = test_data_directory / "fake_path.csv"
    expected_log = f"No data to write to {report_path}"

    with caplog.at_level(logging.INFO):
        mock_open: MagicMock = mocker.mock_open()
        mocker.patch("builtins.open", mock_open)
        mocker.patch("os.makedirs")

        reporter.output_csv(report_path)

        mock_open.assert_not_called()
        assert expected_log in caplog.text


@pytest.mark.parametrize(
    "fixture, last_update_return_value",
    [
        ("results_artifact_data", []),
        ("results_artifact_data", [{"last_update": "2023-01-01T00:00:00Z"}]),
        ("results_metadata_data", []),
        ("results_metadata_data", [{"last_update": "2023-01-01T00:00:00Z"}]),
        ("results_artifact_and_metadata_data", []),
        ("results_artifact_and_metadata_data", [{"last_update": "2023-01-01T00:00:00Z"}]),
    ],
    ids=[
        "artifact_test_results_new_table",
        "artifact_test_results_existing_table",
        "metadata_test_results_new_table",
        "metadata_test_results_existing_table",
        "artifact_metadata_test_results_new_table",
        "artifact_metadata_test_results_existing_table",
    ],
)
def test_suite_reporter_update_table_with_new_results(
    mocker: MockerFixture,
    config: ConfigValues,
    fixture: str,
    request: pytest.FixtureRequest,
    last_update_return_value: list[dict[str, str]],
) -> None:
    """Test SuiteReporter update_table method with new test results.

    Args:
        mocker (MockerFixture): pytest_mock fixture for mocking.
        config (ConfigValues): pytest fixture for common config values.
        fixture (str): The name of the fixture with coverage sample data.
        request (FixtureRequest): A pytest request object for accessing fixtures.
        last_update_return_value (list[dict[str, str]]): Value returned by get_last_update mock
    """
    results_data: SampleResultsData = request.getfixturevalue(fixture)

    get_last_update_query_mock = mocker.MagicMock()
    get_last_update_query_mock.result.return_value = last_update_return_value
    check_rows_exist_query_mock = mocker.MagicMock()
    check_rows_exist_query_mock.result.return_value = []
    client_mock = mocker.MagicMock()
    client_mock.query.side_effect = [get_last_update_query_mock, check_rows_exist_query_mock]
    client_mock.insert_rows_json.return_value = []

    expected_table_id = f"{config.project_id}.{config.dataset_name}.{config.repository}_results"

    reporter = SuiteReporter(
        config.repository,
        config.workflow,
        config.test_suite,
        results_data.metadata_list,
        results_data.artifact_list,
    )

    reporter.update_table(client_mock, config.project_id, config.dataset_name)

    client_mock.insert_rows_json.assert_called_once_with(expected_table_id, results_data.json_rows)


@pytest.mark.parametrize(
    "fixture",
    ["results_artifact_data", "results_metadata_data", "results_artifact_and_metadata_data"],
    ids=["artifact_test_results", "metadata_test_results", "artifact_metadata_test_results"],
)
def test_suite_reporter_update_table_with_new_results_and_row_duplication(
    caplog: LogCaptureFixture,
    mocker: MockerFixture,
    config: ConfigValues,
    fixture: str,
    request: pytest.FixtureRequest,
) -> None:
    """Test SuiteReporter update_table method with new test results, but a duplicate is found before
       insertion.

    Args:
        caplog (LogCaptureFixture): pytest fixture for capturing log output.
        mocker (MockerFixture): pytest_mock fixture for mocking.
        config (ConfigValues): pytest fixture for common config values.
        fixture (str): The name of the fixture with coverage sample data.
        request (FixtureRequest): A pytest request object for accessing fixtures.
    """
    results_data: SampleResultsData = request.getfixturevalue(fixture)

    get_last_update_query_mock = mocker.MagicMock()
    get_last_update_query_mock.result.return_value = [{"last_update": "2024-01-01T00:00:00Z"}]
    check_rows_exist_query_mock = mocker.MagicMock()
    check_rows_exist_query_mock.result.return_value = [{"1": 1}]
    client_mock = mocker.MagicMock()
    client_mock.query.side_effect = [get_last_update_query_mock, check_rows_exist_query_mock]

    expected_log = (
        f"Detected one or more results from "
        f"{config.repository}/{config.workflow}/{config.test_suite} already exist in table "
        f"{config.project_id}.{config.dataset_name}.{config.repository}_results. Aborting insert."
    )

    reporter = SuiteReporter(
        config.repository,
        config.workflow,
        config.test_suite,
        results_data.metadata_list,
        results_data.artifact_list,
    )

    with caplog.at_level(logging.WARNING):
        reporter.update_table(client_mock, config.project_id, config.dataset_name)

        assert expected_log in caplog.text


@pytest.mark.parametrize(
    "fixture",
    ["results_artifact_data", "results_metadata_data", "results_artifact_and_metadata_data"],
    ids=["artifact_test_results", "metadata_test_results", "artifact_metadata_test_results"],
)
def test_suite_reporter_update_table_without_new_test_results(
    caplog: LogCaptureFixture,
    mocker: MockerFixture,
    config: ConfigValues,
    fixture: str,
    request: pytest.FixtureRequest,
) -> None:
    """Test SuiteReporter update_table method with old test results.

    Args:
        caplog (LogCaptureFixture): pytest fixture for capturing log output.
        mocker (MockerFixture): pytest_mock fixture for mocking.
        config (ConfigValues): pytest fixture for common config values.
        fixture (str): The name of the fixture with coverage sample data.
        request (FixtureRequest): A pytest request object for accessing fixtures.
    """
    results_data: SampleResultsData = request.getfixturevalue(fixture)

    get_last_update_query_mock = mocker.MagicMock()
    get_last_update_query_mock.result.return_value = [{"last_update": "2024-01-06T00:00:00Z"}]
    mock_client = mocker.MagicMock()
    mock_client.query.return_value = get_last_update_query_mock

    expected_log = (
        f"There are no new results for {config.repository}/{config.workflow}/{config.test_suite} "
        f"to add to {config.project_id}.{config.dataset_name}.{config.repository}_results."
    )

    reporter = SuiteReporter(
        config.repository,
        config.workflow,
        config.test_suite,
        results_data.metadata_list,
        results_data.artifact_list,
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
    metadata_list: list[CircleCIJobTestMetadata] | None = None
    artifact_list: list[JUnitXmlJobTestSuites] | None = None

    client_mock = mocker.MagicMock()

    expected_log = (
        f"There are no results for {config.repository}/{config.workflow}/{config.test_suite} to "
        f"add to {config.project_id}.{config.dataset_name}.{config.repository}_results."
    )

    reporter = SuiteReporter(
        config.repository, config.workflow, config.test_suite, metadata_list, artifact_list
    )

    with caplog.at_level(logging.INFO):
        reporter.update_table(client_mock, config.project_id, config.dataset_name)

        assert client_mock.mock_calls == [], "Expected no interactions with the mock client."
        assert expected_log in caplog.text
