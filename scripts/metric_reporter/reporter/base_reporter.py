# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""Module defining the base for all reporting in the Metric Reporter."""

import csv
import logging
from pathlib import Path
from typing import Any, Sequence

from dateutil import parser
from pydantic import BaseModel

from scripts.metric_reporter.constants import DATE_FORMAT


class ReporterResultBase(BaseModel):
    """Base class for reporter results."""

    def dict_with_fieldnames(self) -> dict[str, Any]:
        """Convert the result to a dictionary with field names.

        Returns:
            dict[str, Any]: Dictionary representation of the result.
        """
        raise NotImplementedError("Subclasses must implement this method.")


class ReporterError(Exception):
    """Exception raised for errors in the reporter."""

    pass


class BaseReporter:
    """Base class for reporters."""

    logger = logging.getLogger(__name__)
    results: Sequence[ReporterResultBase] = []

    @staticmethod
    def _extract_date(timestamp: str) -> str:
        try:
            datetime = parser.parse(timestamp)
            return datetime.strftime(DATE_FORMAT)
        except (ValueError, TypeError) as error:
            raise ReporterError(f"Invalid timestamp format: {timestamp}") from error

    def output_csv(self, report_path: Path) -> None:
        """Output the results to a CSV file.

        Args:
            report_path (Path): Path to the file where the CSV report will be saved.

        Raises:
            ReporterError: If the report file cannot be created or written to.
        """
        try:
            report_path.parent.mkdir(parents=True, exist_ok=True)
            if not self.results:
                self.logger.warning(f"No data to write to {report_path}.")
                return

            fieldnames: list[str] = list(self.results[0].dict_with_fieldnames().keys())
            with open(report_path, "w", newline="") as csv_file:
                writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
                writer.writeheader()
                for result in self.results:
                    writer.writerow(result.dict_with_fieldnames())

            self.logger.info(f"CSV report written to {report_path}")
        except (OSError, IOError) as error:
            error_mapping: dict[type, str] = {
                OSError: "Error creating directories for the report file",
                IOError: "The report file cannot be created or written to",
            }
            error_msg: str = next(m for t, m in error_mapping.items() if isinstance(error, t))
            self.logger.error(error_msg, exc_info=error)
            raise ReporterError(error_msg) from error

    def update_table(self, client, project_id: str, dataset_name: str) -> None:
        """Update the BigQuery table.

        Args:
            client (Client): The client to interact with BigQuery.
            project_id (str): The BigQuery project ID.
            dataset_name (str): The BigQuery dataset name.

        Raises:
            NotImplementedError: If the method is not implemented by a subclass.
        """
        raise NotImplementedError("Subclasses must implement the `update_bigtable` method.")
