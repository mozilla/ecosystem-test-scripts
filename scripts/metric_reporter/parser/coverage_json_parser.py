# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""Module for parsing coverage json files."""

import logging
import json
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

    meta: PytestMeta
    totals: PytestTotals


class CoverageSummary(BaseModel):
    """A summary of coverage values for a test suite."""

    job: int
    timestamp: str | None = None  # unavailable in llvm-cov
    line_count: int | None
    line_covered: int | None
    line_not_covered: int | None
    line_excluded: int | None = None  # pytest only
    line_percent: float | None
    function_count: int | None = None  # llvm-cov only
    function_covered: int | None = None  # llvm-cov only
    function_not_covered: int | None = None  # llvm-cov only
    function_percent: float | None = None  # llvm-cov only
    branch_count: int | None
    branch_covered: int | None
    branch_not_covered: int | None
    branch_percent: float | None


class CoverageJsonParser:
    """Parses coverage JSON files."""

    logger = logging.getLogger(__name__)

    def _parse_json_data(
        self,
        artifact_file_path: Path,
        job_number: int,
        job_timestamp: str,
        json_data: dict[str, Any],
    ) -> CoverageSummary:
        if "type" in json_data and json_data["type"] == "llvm.coverage.json.export":
            return self._parse_llvm_cov_json_data(
                artifact_file_path, job_number, job_timestamp, json_data
            )
        elif "meta" in json_data:
            return self._parse_pytest_json_data(job_number, json_data)
        else:
            raise ParserError(f"Unknown JSON format for {artifact_file_path}")

    @staticmethod
    def _parse_llvm_cov_json_data(
        artifact_file_path: Path, job_number: int, job_timestamp: str, json_data: dict[str, Any]
    ) -> CoverageSummary:
        llvm_cov_report = LlvmCovReport(**json_data)
        if not len(llvm_cov_report.data) == 1:
            raise ParserError(
                f"The {artifact_file_path} has an unexpected number of items in 'data'."
            )
        totals: LlvmCovTotals = llvm_cov_report.data[0].totals

        coverage_json = CoverageSummary(
            job=job_number,
            timestamp=job_timestamp,
            line_count=totals.lines.count,
            line_covered=totals.lines.covered,
            line_not_covered=totals.lines.count - totals.lines.covered,
            line_percent=totals.lines.percent,
            function_count=totals.functions.count,
            function_covered=totals.functions.covered,
            function_not_covered=totals.functions.count - totals.functions.covered,
            function_percent=totals.functions.percent,
            branch_count=totals.branches.count,
            branch_covered=totals.branches.covered,
            branch_not_covered=totals.branches.count - totals.branches.covered,
            branch_percent=totals.branches.percent,
        )
        return coverage_json

    @staticmethod
    def _parse_pytest_json_data(job_number: int, json_data: dict[str, Any]) -> CoverageSummary:
        pytest_report = PytestReport(**json_data)
        totals: PytestTotals = pytest_report.totals
        coverage_json = CoverageSummary(
            job=job_number,
            timestamp=pytest_report.meta.timestamp,
            line_count=totals.num_statements,
            line_covered=totals.covered_lines,
            line_not_covered=totals.missing_lines,
            line_excluded=totals.excluded_lines,
            line_percent=totals.percent_covered,
            branch_count=totals.num_branches,
            branch_covered=totals.covered_branches,
            branch_not_covered=totals.missing_branches,
            branch_percent=(totals.covered_branches / totals.num_branches) * 100
            if totals.num_branches
            else 0.0,
        )
        return coverage_json

    def parse(self, artifact_path: Path) -> list[CoverageSummary]:
        """Parse coverage JSON data from the specified directory.

        Args:
            artifact_path (Path): The path to the directory containing the coverage files.

        Returns:
            list[]: A list of  objects.

        Raises:
            ParserError: If there are errors reading files, or if there are issues with parsing the
                         JSON data.
        """
        artifact_list: list[CoverageSummary] = []
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
                        coverage_json: CoverageSummary = self._parse_json_data(
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
