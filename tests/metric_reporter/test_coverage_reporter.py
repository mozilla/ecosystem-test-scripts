# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""Tests for the CoverageReporter module."""

import logging
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from pytest import LogCaptureFixture
from pytest_mock import MockerFixture

from scripts.metric_reporter.parser.coverage_json_parser import LlvmCovReport, PytestReport
from scripts.metric_reporter.reporter.coverage_reporter import (
    CoverageReporter,
    CoverageReporterResult,
)
from tests.metric_reporter.conftest import SampleCoverageData


@pytest.mark.parametrize(
    "fixture", ["coverage_llvm_cov_data", "coverage_pytest_data"], ids=["llvm-cov", "pytest"]
)
def test_coverage_reporter_init(fixture: str, request: pytest.FixtureRequest) -> None:
    """Test CoverageReporter initialization with llvm-cov and pytest report data.

    Args:
        fixture (str): The name of the fixture with coverage sample data.
        request (FixtureRequest): A pytest request object for accessing fixtures.
    """
    coverage_data: SampleCoverageData = request.getfixturevalue(fixture)
    expected_results: list[CoverageReporterResult] = coverage_data.report_results
    repository = "repo"
    workflow = "main"
    test_suite = "suite"

    reporter = CoverageReporter(repository, workflow, test_suite, coverage_data.report_list)

    assert reporter.results == expected_results


@pytest.mark.parametrize(
    "fixture", ["coverage_llvm_cov_data", "coverage_pytest_data"], ids=["llvm-cov", "pytest"]
)
def test_coverage_reporter_output_csv(
    fixture: str, request: pytest.FixtureRequest, test_data_directory: Path, mocker: MockerFixture
) -> None:
    """Test CoverageReporter output_results_csv method with llvm-cov and pytest report data.

    Args:
        fixture (str): The name of the fixture with coverage sample data.
        request (FixtureRequest): A pytest request object for accessing fixtures.
        test_data_directory (Path): Test data directory for the Metric Reporter.
        mocker (MockerFixture): pytest_mock fixture for mocking.
    """
    repository = "repo"
    workflow = "main"
    test_suite = "suite"
    coverage_data: SampleCoverageData = request.getfixturevalue(fixture)
    expected_csv: str = coverage_data.csv
    reporter = CoverageReporter(repository, workflow, test_suite, coverage_data.report_list)
    report_path = test_data_directory / "fake_path.csv"

    mock_open: MagicMock = mocker.mock_open()
    mocker.patch("builtins.open", mock_open)
    mocker.patch("os.makedirs")

    reporter.output_csv(report_path)

    mock_open.assert_called_once_with(report_path, "w", newline="")
    handle = mock_open()
    actual_csv = "".join(call[0][0] for call in handle.write.call_args_list)
    assert actual_csv == expected_csv


def test_coverage_reporter_output_csv_with_empty_test_results(
    test_data_directory: Path, caplog: LogCaptureFixture, mocker: MockerFixture
) -> None:
    """Test CoverageReporter output_results_csv method with no test results.

    Args:
        test_data_directory (Path): Test data directory for the Metric Reporter.
        caplog (LogCaptureFixture): pytest fixture for capturing log output.
        mocker (MockerFixture): pytest_mock fixture for mocking.
    """
    repository = "repo"
    workflow = "main"
    test_suite = "suite"
    coverage_summary_list: list[LlvmCovReport | PytestReport] | None = None
    reporter = CoverageReporter(repository, workflow, test_suite, coverage_summary_list)
    report_path = test_data_directory / "fake_path.csv"
    expected_log = f"No data to write to {report_path}"

    with caplog.at_level(logging.INFO):
        mock_open: MagicMock = mocker.mock_open()
        mocker.patch("builtins.open", mock_open)
        mocker.patch("os.makedirs")

        reporter.output_csv(report_path)

        mock_open.assert_not_called()
        assert expected_log in caplog.text
