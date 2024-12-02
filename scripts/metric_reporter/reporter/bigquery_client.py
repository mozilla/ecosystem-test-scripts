# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""BigQuery client"""

import logging
from datetime import datetime, date

from google.api_core.exceptions import GoogleAPIError, NotFound
from google.cloud import bigquery
from google.oauth2 import service_account

from scripts.metric_reporter.constants import DATETIME_FORMAT


class BigQueryClientError(Exception):
    """Custom exception for BigQuery client errors."""

    pass


class BigQueryClient:
    """BigQuery client class to interact with BigQuery dataset for test metrics."""

    logger = logging.getLogger(__name__)

    def __init__(self, project_id: str, dataset_name: str, service_account_file: str) -> None:
        """Initialize the BigQuery client.

        Args:
            project_id (str): The BigQuery project ID.
            dataset_name (str): The BigQuery dataset name.
            service_account_file (str): The file path to service credential JSON.
        """
        credentials = service_account.Credentials.from_service_account_file(service_account_file)  # type: ignore
        self.client = bigquery.Client(credentials=credentials, project=project_id)
        self.project_id = project_id
        self.dataset_name = dataset_name

    def get_averages_last_update_date(self, table_name: str) -> date | None:
        """Get the date of the last update in the specified averages table.

        Args:
            table_name (str): The name of the table to query.

        Returns:
            datetime | None: The date of the last row in the table, or None if the table is empty.
        """
        query = f"""
            SELECT GREATEST(MAX(`End Date 30`), MAX(`End Date 60`), MAX(`End Date 90`)) as last_update 
            FROM `{self.project_id}.{self.dataset_name}.{table_name}`
        """  # nosec
        try:
            query_job = self.client.query(query)
            result = query_job.result()
            for row in result:
                last_update: date | None = row["last_update"]
                return last_update
        except (GoogleAPIError, NotFound) as error:
            error_mapping: dict[type, str] = {
                GoogleAPIError: f"Error executing query: {query}",
                NotFound: f"Dataset or Table not found for query: {query}",
            }
            error_msg: str = next(m for t, m in error_mapping.items() if isinstance(error, t))
            self.logger.error(error_msg, exc_info=error)
            raise BigQueryClientError(error_msg) from error

    def get_last_update_timestamp(self, table_name: str) -> datetime | None:
        """Get the timestamp of the last update in the specified coverage or results table.

        Args:
            table_name (str): The name of the table to query.

        Returns:
            datetime | None: The timestamp of the last row in the table, or None if the table is empty.
        """
        query = f"""
            SELECT FORMAT_TIMESTAMP('{DATETIME_FORMAT}', MAX(`Timestamp`)) as last_update 
            FROM `{self.project_id}.{self.dataset_name}.{table_name}`
        """  # nosec
        try:
            query_job = self.client.query(query)
            result = query_job.result()
            for row in result:
                last_update: str | None = row["last_update"]
                return datetime.strptime(last_update, DATETIME_FORMAT) if last_update else None
        except (GoogleAPIError, NotFound) as error:
            error_mapping: dict[type, str] = {
                GoogleAPIError: f"Error executing query: {query}",
                NotFound: f"Dataset or Table not found for query: {query}",
            }
            error_msg: str = next(m for t, m in error_mapping.items() if isinstance(error, t))
            self.logger.error(error_msg, exc_info=error)
            raise BigQueryClientError(error_msg) from error
