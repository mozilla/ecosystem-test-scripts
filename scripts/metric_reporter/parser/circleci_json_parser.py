# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""Module for parsing test suite results from CircleCI metadata."""

import json
import logging
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ValidationError

from scripts.metric_reporter.parser.base_parser import ParserError


class CircleCIJob(BaseModel):
    """Represents a CircleCI job with its metadata."""

    dependencies: list[Any]
    job_number: int
    id: str
    started_at: str
    name: str
    project_slug: str
    status: str
    type: str
    stopped_at: str


class CircleCITestMetadata(BaseModel):
    """Represents test metadata for a CircleCI job."""

    classname: str
    name: str
    result: str
    message: str
    run_time: float
    source: str


class CircleCIJobTestMetadata(BaseModel):
    """Represents the test suite results for a CircleCI job."""

    job: CircleCIJob
    test_metadata: list[CircleCITestMetadata] | None = None


class CircleCIJsonParser:
    """Parses CircleCI JSON test metadata files."""

    logger = logging.getLogger(__name__)

    def parse(self, metadata_path: Path) -> list[CircleCIJobTestMetadata]:
        """Parse CircleCI JSON test metadata from the specified directory.

        Args:
            metadata_path (Path): The path to the directory containing the test metadata files.

        Returns:
            list[CircleCIJobTestMetadata]: A list of CircleCIJobTestMetadata objects.

        Raises:
            ParserError: If there are errors reading files, or if there are issues with parsing the
                         JSON data.
        """
        metadata_list: list[CircleCIJobTestMetadata] = []
        metadata_file_paths: list[Path] = sorted(metadata_path.glob("*.json"))
        for metadata_file_path in metadata_file_paths:
            self.logger.info(f"Parsing {metadata_file_path}")
            try:
                with metadata_file_path.open() as file:
                    data: dict[str, Any] = json.load(file)
                    metadata = CircleCIJobTestMetadata(**data)
                    metadata_list.append(metadata)
            except (OSError, json.JSONDecodeError, ValidationError) as error:
                error_mapping: dict[type, str] = {
                    OSError: f"Error reading the file {metadata_file_path}",
                    json.JSONDecodeError: f"Invalid JSON format for file {metadata_file_path}",
                    ValidationError: f"Unexpected value or schema in file {metadata_file_path}",
                }
                error_msg: str = next(m for t, m in error_mapping.items() if isinstance(error, t))
                self.logger.error(error_msg, exc_info=error)
                raise ParserError(error_msg) from error
        return metadata_list
