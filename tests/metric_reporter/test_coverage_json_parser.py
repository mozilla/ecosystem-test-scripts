# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""Tests for the CoverageJsonParser module."""

import pytest
from pytest_mock import MockerFixture

from scripts.metric_reporter.parser.coverage_json_parser import (
    CoverageJsonGroup,
    CoverageJsonParser,
)
from tests.metric_reporter.conftest import SampleCoverageData


@pytest.mark.parametrize(
    "fixture", ["coverage_llvm_cov_data", "coverage_pytest_data"], ids=["llvm-cov", "pytest"]
)
def test_parse(mocker: MockerFixture, fixture: str, request: pytest.FixtureRequest) -> None:
    """Test CoverageJsonParser parse method with llvm-cov and pytest report data.

    Args:
        mocker (MockerFixture): pytest_mock fixture for mocking.
        fixture (str): The name of the fixture with coverage sample data.
        request (FixtureRequest): A pytest request object for accessing fixtures.
    """
    coverage_data: SampleCoverageData = request.getfixturevalue(fixture)
    expected_results: list[CoverageJsonGroup] = [coverage_data.coverage_json_group]
    gcs_client_mock = mocker.MagicMock()
    gcs_client_mock.get_coverage_artifact_content.side_effect = (
        lambda repository, artifact_file_name: (
            coverage_data.sample_directory / artifact_file_name
        ).read_text()
    )
    parser = CoverageJsonParser(gcs_client_mock)

    actual_results: list[CoverageJsonGroup] = parser.parse(coverage_data.sample_files)

    assert actual_results == expected_results
