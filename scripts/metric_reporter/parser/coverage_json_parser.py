# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""Module for parsing coverage json files."""

import json
import logging
from json import JSONDecodeError
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ValidationError

from scripts.metric_reporter.parser.base_parser import ParserError, JOB_DIRECTORY_PATTERN


class LlvmCovStats(BaseModel):
    """Represents coverage values in a llvm-cov report."""

    count: int
    covered: int
    percent: float


class LlvmCovTotals(BaseModel):
    """Represents coverage total categories in a llvm-cov report."""

    branches: LlvmCovStats
    functions: LlvmCovStats
    instantiations: LlvmCovStats
    lines: LlvmCovStats
    mcdc: LlvmCovStats
    regions: LlvmCovStats


class LlvmCovDataItem(BaseModel):
    """Represents a data item in a llvm-cov report."""

    totals: LlvmCovTotals


class LlvmCovReport(BaseModel):
    """Represents the llvm-cov report."""

    job_number: int
    job_timestamp: str | None
    data: list[LlvmCovDataItem]
    type: str
    version: str


class PytestMeta(BaseModel):
    """Represents metadata values in a pytest coverage report."""

    format: int
    version: str
    timestamp: str
    branch_coverage: bool
    show_contexts: bool


class PytestTotals(BaseModel):
    """Represents coverage values in a pytest coverage report."""

    num_statements: int
    covered_lines: int
    missing_lines: int
    excluded_lines: int
    percent_covered: float
    percent_covered_display: str
    num_branches: int
    covered_branches: int
    num_partial_branches: int
    missing_branches: int


class PytestReport(BaseModel):
    """Represents a pytest coverage report."""

    job_number: int
    job_timestamp: str | None
    meta: PytestMeta
    totals: PytestTotals


class CoverageJsonParser:
    """Parses coverage JSON files."""

    logger = logging.getLogger(__name__)

    @staticmethod
    def _parse_json_data(
        artifact_file_path: Path,
        job_number: int,
        job_timestamp: str,
        json_data: dict[str, Any],
    ) -> LlvmCovReport | PytestReport:
        if "type" in json_data and json_data["type"] == "llvm.coverage.json.export":
            return LlvmCovReport(job_number=job_number, job_timestamp=job_timestamp, **json_data)
        elif "meta" in json_data:
            return PytestReport(job_number=job_number, job_timestamp=job_timestamp, **json_data)
        else:
            raise ParserError(f"Unknown JSON format for {artifact_file_path}")

    def parse(self, artifact_path: Path) -> list[LlvmCovReport | PytestReport]:
        """Parse coverage JSON data from the specified directory.

        Args:
            artifact_path (Path): The path to the directory containing the coverage files.

        Returns:
            list[LlvmCovReport | PytestReport]: A list of coverage report objects.

        Raises:
            ParserError: If there are errors reading files, or if there are issues with parsing the
                         JSON data.
        """
        artifact_list: list[LlvmCovReport | PytestReport] = []
        job_paths: list[Path] = sorted(artifact_path.iterdir())
        for job_path in job_paths:
            if match := JOB_DIRECTORY_PATTERN.match(job_path.name):
                job_number = int(match.group("job_number"))
                job_timestamp = match.group("job_timestamp")
            else:
                raise ParserError(f"Unexpected job_path format: {job_path.name}")

            artifact_file_paths: list[Path] = sorted(job_path.glob("*.json"))
            for artifact_file_path in artifact_file_paths:
                self.logger.info(f"Parsing {artifact_file_path}")
                try:
                    with artifact_file_path.open() as json_file:
                        json_data: dict[str, Any] = json.load(json_file)
                        coverage_json: LlvmCovReport | PytestReport = self._parse_json_data(
                            artifact_file_path, job_number, job_timestamp, json_data
                        )
                        artifact_list.append(coverage_json)
                except (OSError, JSONDecodeError, ValidationError) as error:
                    error_mapping: dict[type, str] = {
                        OSError: f"Error reading the file {artifact_file_path}",
                        JSONDecodeError: f"Invalid JSON format for file {artifact_file_path}",
                        ValidationError: f"Unexpected value or schema in file {artifact_file_path}",
                    }
                    error_msg: str = next(
                        m for t, m in error_mapping.items() if isinstance(error, t)
                    )
                    self.logger.error(error_msg, exc_info=error)
                    raise ParserError(error_msg) from error
        return artifact_list
