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

from scripts.test_metric_reporter.suite_reporter import SuiteReporter, SuiteReporterResult

TEST_METADATA_DIRECTORY_EMPTY_TEST_RESULTS = "test_metadata_directory_empty_test_results"
TEST_METADATA_DIRECTORY_TEST_RESULTS = "test_metadata_directory_test_results"


@pytest.fixture
def test_data_directory() -> Path:
    """Provide the base path to the test data directory."""
    return Path(__file__).parent / "test_data"


@pytest.mark.parametrize(
    "test_directory, expected_results",
    [
        (
            TEST_METADATA_DIRECTORY_TEST_RESULTS,
            [
                SuiteReporterResult(
                    date="2024-01-01",
                    job=1,
                    status="failure",
                    execution_time=3600.0,
                    success=0,
                    failure=1,
                    skipped=0,
                    unknown=0,
                ),
                SuiteReporterResult(
                    date="2024-01-02",
                    job=2,
                    status="success",
                    execution_time=3600.0,
                    success=0,
                    failure=0,
                    skipped=1,
                    unknown=0,
                ),
                SuiteReporterResult(
                    date="2024-01-03",
                    job=3,
                    status="success",
                    execution_time=3600.0,
                    success=1,
                    failure=0,
                    skipped=0,
                    unknown=0,
                ),
                SuiteReporterResult(
                    date="2024-01-04",
                    job=4,
                    status="success",
                    execution_time=3600.0,
                    success=0,
                    failure=0,
                    skipped=0,
                    unknown=1,
                ),
                SuiteReporterResult(
                    date="2024-01-05",
                    job=5,
                    status="success",
                    execution_time=3600.0,
                    success=1,
                    failure=0,
                    skipped=0,
                    unknown=0,
                ),
            ],
        ),
        (TEST_METADATA_DIRECTORY_EMPTY_TEST_RESULTS, []),
    ],
    ids=["with_test_results", "with_empty_test_results"],
)
def test_suite_reporter_init(
    test_data_directory: Path, test_directory: str, expected_results: list[SuiteReporterResult]
) -> None:
    """Test SuiteReporter initialization with various test data.

    Args:
        test_data_directory (Path): Base directory containing test data files.
        test_directory (str): Specific test data directory to load.
        expected_results (list[SuiteReporterResult]): Expected results from the SuiteReporter.
    """
    test_metadata_directory = str(test_data_directory / test_directory)

    reporter = SuiteReporter(test_metadata_directory)

    assert reporter.metadata_results == expected_results


def test_suite_reporter_output_csv_with_test_results(
    test_data_directory: Path, mocker: MockerFixture
) -> None:
    """Test SuiteReporter output_results_csv method with test results.

    Args:
        test_data_directory (Path): Base directory containing test data files.
        mocker (MockerFixture): pytest_mock fixture for mocking.
    """
    test_metadata_directory = str(test_data_directory / TEST_METADATA_DIRECTORY_TEST_RESULTS)
    reporter = SuiteReporter(test_metadata_directory)
    report_path = "fake_path.csv"
    expected_csv = (
        "Date - Job Number,Date,Job Number,Status,Execution Time,Success,Failure,Skipped,Unknown,"
        "Total,Success Rate (%),Failure Rate (%),Skipped Rate (%),Unknown Rate (%)\r\n"
        "2024-01-01 - 1,2024-01-01,1,failure,3600.0,0,1,0,0,1,0.0,100.0,0.0,0.0\r\n"
        "2024-01-02 - 2,2024-01-02,2,success,3600.0,0,0,1,0,1,0.0,0.0,100.0,0.0\r\n"
        "2024-01-03 - 3,2024-01-03,3,success,3600.0,1,0,0,0,1,100.0,0.0,0.0,0.0\r\n"
        "2024-01-04 - 4,2024-01-04,4,success,3600.0,0,0,0,1,1,0.0,0.0,0.0,100.0\r\n"
        "2024-01-05 - 5,2024-01-05,5,success,3600.0,1,0,0,0,1,100.0,0.0,0.0,0.0\r\n"
    )

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
        test_data_directory (Path): Base directory containing test data files.
        caplog (LogCaptureFixture): pytest fixture for capturing log output.
        mocker (MockerFixture): pytest_mock fixture for mocking.
    """
    test_metadata_directory = str(test_data_directory / TEST_METADATA_DIRECTORY_EMPTY_TEST_RESULTS)
    reporter = SuiteReporter(test_metadata_directory)
    report_path = "fake_path.csv"
    expected_log = "No data to write to the CSV file."

    with caplog.at_level(logging.INFO):
        mock_open: MagicMock = mocker.mock_open()
        mocker.patch("builtins.open", mock_open)
        mocker.patch("os.makedirs")

        reporter.output_results_csv(report_path)

        mock_open.assert_not_called()
        assert expected_log in caplog.text
