# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""Module defining the Report Merger."""

import csv
import logging
from pathlib import Path
from typing import Any

from pydantic import BaseModel


class MergedReport(BaseModel):
    """Represents the merged report data."""

    header: Any
    rows: Any


class ReportMergerError(Exception):
    """Exception raised for errors in the merger."""

    pass


class ReportMerger:
    """Report Merger."""

    logger = logging.getLogger(__name__)

    def __init__(
        self,
        reports_paths: list[Path],
    ) -> None:
        """Initialize the merger with list of reports to merge.

        Args:
            reports_paths: list[Path]: The list of reports to merge.
        """
        super().__init__()
        self.merged_report = self._merge(reports_paths)

    @staticmethod
    def _merge(reports_paths: list[Path]) -> MergedReport:
        rows = []
        header = None
        for report_path in reports_paths:
            with open(report_path, mode="r") as report_file:
                reader = csv.DictReader(report_file)
                if header is None:
                    header = reader.fieldnames
                for row in reader:
                    rows.append(row)

        return MergedReport(header=header, rows=rows)

    def output_csv(self, report_path: Path) -> None:
        """Output the results to a CSV file.

        Args:
            report_path (Path): Path to the file where the CSV report will be saved.

        Raises:
            ReportMergerError: If the report file cannot be created or written to.
        """
        try:
            report_path.parent.mkdir(parents=True, exist_ok=True)
            if not self.merged_report:
                self.logger.warning(f"No data to write to {report_path}.")
                return

            with open(report_path, mode="w", newline="") as csv_file:
                writer = csv.DictWriter(csv_file, fieldnames=self.merged_report.header)
                writer.writeheader()
                writer.writerows(self.merged_report.rows)

            self.logger.info(f"CSV report written to {report_path}")
        except (OSError, IOError) as error:
            error_mapping: dict[type, str] = {
                OSError: "Error creating directories for the report file",
                IOError: "The report file cannot be created or written to",
            }
            error_msg: str = next(m for t, m in error_mapping.items() if isinstance(error, t))
            self.logger.error(error_msg, exc_info=error)
            raise ReportMergerError(error_msg) from error
