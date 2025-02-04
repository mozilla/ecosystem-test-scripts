# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""Tests for the CoverageJsonParser module."""

import pytest

from scripts.metric_reporter.parser.coverage_json_parser import (
    CoverageJsonGroup,
    CoverageJsonParser,
)
from tests.metric_reporter.conftest import SampleCoverageData


@pytest.mark.parametrize(
    "fixture", ["coverage_llvm_cov_data", "coverage_pytest_data"], ids=["llvm-cov", "pytest"]
)
def test_parse(fixture: str, request: pytest.FixtureRequest) -> None:
    """Test CoverageJsonParser parse method with llvm-cov and pytest report data.

    Args:
        fixture (str): The name of the fixture with coverage sample data.
        request (FixtureRequest): A pytest request object for accessing fixtures.
    """
    coverage_data: SampleCoverageData = request.getfixturevalue(fixture)
    expected_results: list[CoverageJsonGroup] = [coverage_data.coverage_json_group]
    parser = CoverageJsonParser()

    actual_results: list[CoverageJsonGroup] = parser.parse(coverage_data.sample_files)

    assert actual_results == expected_results
