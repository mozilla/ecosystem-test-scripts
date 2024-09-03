# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""Tests for the CoverageJsonParser module."""

from pathlib import Path

import pytest

from scripts.metric_reporter.parser.coverage_json_parser import CoverageSummary, CoverageJsonParser

EXPECTED_LLVM_COV: list[CoverageSummary] = [
    CoverageSummary(
        job=1,
        timestamp="2024-08-30T19:56:50Z",
        line_count=9441,
        line_covered=5761,
        line_not_covered=3680,
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

EXPECTED_PYTEST: list[CoverageSummary] = [
    CoverageSummary(
        job=1,
        timestamp="2024-08-29T17:43:41.679830",
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


@pytest.mark.parametrize(
    "artifact_directory, expected_results",
    [
        ("llvm_cov_json_samples", EXPECTED_LLVM_COV),
        ("pytest_json_samples", EXPECTED_PYTEST),
    ],
    ids=["llvm-cov", "pytest"],
)
def test_parse(
    test_data_directory: Path,
    artifact_directory: str,
    expected_results: list[CoverageSummary],
) -> None:
    """Test JUnitXmlParser parse method with various test data.

    Args:
        test_data_directory (Path): Test data directory for the Metric Reporter.
        artifact_directory (str): Test data directory name.
        expected_results (list[CoverageSummary]): Expected results from the CoverageJsonParser.
    """
    artifact_path: Path = test_data_directory / artifact_directory
    parser = CoverageJsonParser()

    actual_results: list[CoverageSummary] = parser.parse(artifact_path)

    assert actual_results == expected_results
