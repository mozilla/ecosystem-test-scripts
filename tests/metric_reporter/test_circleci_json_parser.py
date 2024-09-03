# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""Tests for the CircleCIJsonParser module."""

from pathlib import Path

import pytest

from scripts.metric_reporter.parser.circleci_json_parser import (
    CircleCIJobTestMetadata,
    CircleCITestMetadata,
    CircleCIJob,
    CircleCIJsonParser,
)

EXPECTED_EMPTY: list[CircleCIJobTestMetadata] = [
    CircleCIJobTestMetadata(
        job=CircleCIJob(
            dependencies=[],
            job_number=1,
            id="1",
            started_at="2024-01-01T00:00:00Z",
            name="test-job",
            project_slug="test/test-project",
            status="success",
            type="build",
            stopped_at="2024-01-01T01:00:00Z",
        ),
        test_metadata=[],
    )
]

EXPECTED_FAILURE: list[CircleCIJobTestMetadata] = [
    CircleCIJobTestMetadata(
        job=CircleCIJob(
            dependencies=[],
            job_number=2,
            id="2",
            started_at="2024-01-02T00:00:00Z",
            name="test-job",
            project_slug="test/test-project",
            status="failed",
            type="build",
            stopped_at="2024-01-02T01:00:00Z",
        ),
        test_metadata=[
            CircleCITestMetadata(
                classname="test_class",
                name="test_failure",
                result="failure",
                message="",
                run_time=1.2,
                source="test_source",
            )
        ],
    )
]

EXPECTED_SKIPPED: list[CircleCIJobTestMetadata] = [
    CircleCIJobTestMetadata(
        job=CircleCIJob(
            dependencies=[],
            job_number=3,
            id="3",
            started_at="2024-01-03T00:00:00Z",
            name="test-job",
            project_slug="test/test-project",
            status="success",
            type="build",
            stopped_at="2024-01-03T01:00:00Z",
        ),
        test_metadata=[
            CircleCITestMetadata(
                classname="test_class",
                name="test_skipped",
                result="skipped",
                message="",
                run_time=1.3,
                source="test_source",
            )
        ],
    ),
]

EXPECTED_SUCCESS: list[CircleCIJobTestMetadata] = [
    CircleCIJobTestMetadata(
        job=CircleCIJob(
            dependencies=[],
            job_number=4,
            id="4",
            started_at="2024-01-04T00:00:00Z",
            name="test-job",
            project_slug="test/test-project",
            status="success",
            type="build",
            stopped_at="2024-01-04T01:00:00Z",
        ),
        test_metadata=[
            CircleCITestMetadata(
                classname="test_class",
                name="test_success",
                result="success",
                message="",
                run_time=1.4,
                source="test_source",
            )
        ],
    ),
]

EXPECTED_UNKNOWN: list[CircleCIJobTestMetadata] = [
    CircleCIJobTestMetadata(
        job=CircleCIJob(
            dependencies=[],
            job_number=5,
            id="5",
            started_at="2024-01-05T00:00:00Z",
            name="test-job",
            project_slug="test/test-project",
            status="success",
            type="build",
            stopped_at="2024-01-05T01:00:00Z",
        ),
        test_metadata=[
            CircleCITestMetadata(
                classname="test_class",
                name="test_unknown",
                result="system-err",
                message="",
                run_time=1.5,
                source="test_source",
            )
        ],
    ),
]


@pytest.fixture
def circleci_json_samples_directory(test_data_directory: Path) -> Path:
    """Provide the path to the circleci_json_samples directory."""
    return test_data_directory / "circleci_json_samples"


@pytest.mark.parametrize(
    "metadata_directory, expected_results",
    [
        ("empty", EXPECTED_EMPTY),
        ("failure", EXPECTED_FAILURE),
        ("skipped", EXPECTED_SKIPPED),
        ("success", EXPECTED_SUCCESS),
        ("unknown", EXPECTED_UNKNOWN),
    ],
    ids=["empty", "failure", "skipped", "success", "unknown"],
)
def test_parse(
    circleci_json_samples_directory: Path,
    metadata_directory: str,
    expected_results: list[CircleCIJobTestMetadata],
) -> None:
    """Test CircleCIJsonParser parse method with various test data.

    Args:
        circleci_json_samples_directory (Path): circleci_json_samples directory path.
        metadata_directory (str): Test data directory name.
        expected_results (list[CircleCIJobTestMetadata]): Expected results from the
                                                          CircleCIJsonParser.
    """
    metadata_path: Path = circleci_json_samples_directory / metadata_directory
    parser = CircleCIJsonParser()

    actual_results: list[CircleCIJobTestMetadata] = parser.parse(metadata_path)

    assert actual_results == expected_results
