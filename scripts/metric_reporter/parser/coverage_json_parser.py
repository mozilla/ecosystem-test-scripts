# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""Module for parsing coverage json files."""

import json
import logging
from json import JSONDecodeError
from typing import Any

from pydantic import BaseModel, ValidationError

from scripts.metric_reporter.gcs_client import GCSClient
from scripts.metric_reporter.parser.base_parser import BaseParser, ParserError, ArtifactFile
from scripts.metric_reporter.parser.coverage_json_jest_parser import JestJsonParser


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
    job_timestamp: str
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
    job_timestamp: str
    meta: PytestMeta
    totals: PytestTotals


class JestCovDetails(BaseModel):
    """Represents coverage values from a Jest coverage report."""

    count: int
    percent: float
    covered: int
    not_covered: int


class JestCovTotals(BaseModel):
    """Represents coverage totals from a Jest coverage report."""

    statement: JestCovDetails
    function: JestCovDetails
    branch: JestCovDetails
    line: JestCovDetails


class JestCovReport(BaseModel):
    """Represents a Jest coverage report."""

    job_number: int
    job_timestamp: str
    totals: JestCovTotals


CoverageJson = LlvmCovReport | PytestReport | JestCovReport


class CoverageJsonGroup(BaseModel):
    """Represents results from one or more Coverage files for a test suite."""

    repository: str
    workflow: str
    test_suite: str
    coverage_jsons: list[CoverageJson] = []


class CoverageJsonParser(BaseParser):
    """Parses coverage JSON files."""

    logger = logging.getLogger(__name__)

    def __init__(self, gcs_client: GCSClient) -> None:
        """Initialize the CoverageJsonParser.

        Args:
            gcs_client (GCSClient): GCS client.
        """
        self._gcs_client = gcs_client

    @staticmethod
    def _get_coverage_json_group(
        file: ArtifactFile, coverage_json_groups: list[CoverageJsonGroup]
    ) -> CoverageJsonGroup:
        if group := next(
            (
                group
                for group in coverage_json_groups
                if group.repository == file.repository
                and group.workflow == file.workflow
                and group.test_suite == file.test_suite
            ),
            None,
        ):
            if any(
                coverage_json
                for coverage_json in group.coverage_jsons
                if coverage_json.job_number == file.job_number
                and coverage_json.job_timestamp == file.job_timestamp
            ):
                raise ParserError(
                    f"More than one coverage JSON file found for a test suite. "
                    f"Duplicate File: {file.name}."
                )
        else:
            group = CoverageJsonGroup(
                repository=file.repository, workflow=file.workflow, test_suite=file.test_suite
            )
            coverage_json_groups.append(group)
        return group

    @staticmethod
    def _parse_json_data(file: ArtifactFile, json_data: dict[str, Any]) -> CoverageJson:
        if "type" in json_data and json_data["type"] == "llvm.coverage.json.export":
            return LlvmCovReport(
                job_number=file.job_number, job_timestamp=file.job_timestamp, **json_data
            )
        elif "meta" in json_data:
            return PytestReport(
                job_number=file.job_number,
                job_timestamp=file.job_timestamp,
                **json_data,
            )
        elif any(k in next(iter(json_data.values())) for k in ("statementMap")):
            results = JestJsonParser.parse_jest_json(json_data)
            return JestCovReport(
                job_number=file.job_number, job_timestamp=file.job_timestamp, totals=results
            )
        else:
            raise ParserError(f"Unknown JSON format for {file.name}")

    def parse(self, artifact_file_names: list[str]) -> list[CoverageJsonGroup]:
        """Parse coverage JSON data from the specified directory.

        Args:
            artifact_file_names (list[str]): File names of the coverage JSON files.

        Returns:
            list[CoverageJsonGroup]: Parsed coverage JSON files grouped by repository, workflow and
                                     test suite.

        Raises:
            ParserError: If there are errors reading files, or if there are issues with parsing the
                         JSON data.
        """
        coverage_json_groups: list[CoverageJsonGroup] = []
        for artifact_file_name in artifact_file_names:
            self.logger.info(f"Parsing {artifact_file_name}")
            file: ArtifactFile = self._parse_artifact_file_name(artifact_file_name)
            group: CoverageJsonGroup = self._get_coverage_json_group(file, coverage_json_groups)
            try:
                content: str = self._gcs_client.get_coverage_artifact_content(
                    file.repository, artifact_file_name
                )
                json_data: dict[str, Any] = json.loads(content)
                coverage_json: CoverageJson = self._parse_json_data(file, json_data)
                group.coverage_jsons.append(coverage_json)
            except (JSONDecodeError, ValidationError) as error:
                error_mapping: dict[type, str] = {
                    JSONDecodeError: f"Invalid JSON format for file {artifact_file_name}",
                    ValidationError: f"Unexpected value or schema in file {artifact_file_name}",
                }
                error_msg: str = next(m for t, m in error_mapping.items() if isinstance(error, t))
                self.logger.error(error_msg, exc_info=error)
                raise ParserError(error_msg) from error
        return coverage_json_groups
