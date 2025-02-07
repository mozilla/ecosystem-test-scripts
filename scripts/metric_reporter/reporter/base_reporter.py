# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""Module defining the base for all reporting in the Metric Reporter."""

import logging
import re
from typing import Any, Sequence

from dateutil import parser
from google.cloud.bigquery import Client
from pydantic import BaseModel

from scripts.common.constants import DATE_FORMAT


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

    @staticmethod
    def _normalize_name(name: str, delimiter: str = "") -> str:
        normalized = re.sub(r"[^a-zA-Z0-9_]+", delimiter, name).lower()
        return normalized.strip("_")

    def update_table(self, client: Client, project_id: str, dataset_name: str) -> None:
        """Update the BigQuery table.

        Args:
            client (Client): The client to interact with BigQuery.
            project_id (str): The BigQuery project ID.
            dataset_name (str): The BigQuery dataset name.

        Raises:
            NotImplementedError: If the method is not implemented by a subclass.
        """
        raise NotImplementedError("Subclasses must implement the `update_table` method.")
