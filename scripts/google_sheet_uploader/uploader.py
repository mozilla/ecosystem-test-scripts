"""Module containing the GoogleSheetUploader class for uploading CSV data to Google Sheets."""

import os
import pandas as pd
from googleapiclient.discovery import build
from google.oauth2 import service_account
import logging
from typing import Any


class GoogleSheetUploaderError(Exception):
    """Base exception class for GoogleSheetUploader."""

    pass


class CSVFileNotFoundError(GoogleSheetUploaderError):
    """Exception raised when a CSV file is not found."""

    pass


class CSVReadError(GoogleSheetUploaderError):
    """Exception raised when a CSV file cannot be read."""

    pass


class SheetClearError(GoogleSheetUploaderError):
    """Exception raised when clearing a sheet fails."""

    pass


class SheetWriteError(GoogleSheetUploaderError):
    """Exception raised when writing to a sheet fails."""

    pass


class GoogleSheetUploader:
    """Uploads CSV files to specified Google Sheets tabs."""

    def __init__(self, config: Any):
        """Initialize the uploader with configuration and set up Google Sheets service.

        Args:
            config (Config): Configuration object containing mappings and credentials.
        """
        self.config = config
        self.logger = logging.getLogger(__name__)

        try:
            self.credentials = service_account.Credentials.from_service_account_file(
                self.config.service_account_file,
                scopes=["https://www.googleapis.com/auth/spreadsheets"],
            )  # type: ignore
            self.service = build("sheets", "v4", credentials=self.credentials)
        except Exception as e:
            self.logger.error(f"Failed to initialize Google Sheets service: {e}")
            raise GoogleSheetUploaderError(
                "Initialization of Google Sheets service failed."
            ) from e

    def clear_sheet(self, sheet_id: str, tab_name: str):
        """Clear the contents of a specific tab in a Google Sheet.

        Args:
            sheet_id (str): The ID of the Google Sheet.
            tab_name (str): The name of the tab to clear.
        """
        try:
            sheet = self.service.spreadsheets()
            batch_clear_values_request_body = {"ranges": [tab_name]}
            request = sheet.values().batchClear(
                spreadsheetId=sheet_id, body=batch_clear_values_request_body
            )
            response = request.execute()
            return response
        except Exception as e:
            self.logger.error(f"Failed to clear sheet {sheet_id}, tab {tab_name}: {e}")
            raise SheetClearError(f"Failed to clear sheet {sheet_id}, tab {tab_name}") from e

    def write_data_to_sheet(self, sheet_id: str, tab_name: str, data: pd.DataFrame):
        """Write data to a specific tab in a Google Sheet.

        Args:
            sheet_id (str): The ID of the Google Sheet.
            tab_name (str): The name of the tab to write data to.
            data (pd.DataFrame): The pandas DataFrame containing the data to upload.
        """
        try:
            sheet = self.service.spreadsheets()

            # Replace NaN values with empty strings to prevent JSON errors
            data = data.fillna("")

            # Prepare data including headers
            values = [data.columns.values.tolist()] + data.values.tolist()
            body = {"values": values}

            # Update the sheet
            result = (
                sheet.values()
                .update(spreadsheetId=sheet_id, range=tab_name, valueInputOption="RAW", body=body)
                .execute()
            )
            return result
        except Exception as e:
            self.logger.error(f"Failed to write data to sheet {sheet_id}, tab {tab_name}: {e}")
            raise SheetWriteError(
                f"Failed to write data to sheet {sheet_id}, tab {tab_name}"
            ) from e

    def process_csv_files(self):
        """Process each CSV file and upload its content to the corresponding Google Sheet."""
        for sheet_mapping in self.config.mappings:
            sheet_id = sheet_mapping.sheet_id
            for tab in sheet_mapping.tabs:
                csv_file = tab.file_name
                tab_name = tab.tab_name

                self.logger.info(f"Processing {csv_file} -> Sheet ID: {sheet_id}, Tab: {tab_name}")

                # Adjust the path to your CSV files if necessary
                csv_file_path = os.path.join(self.config.reports_dir, csv_file)

                # Check if the CSV file exists
                if not os.path.exists(csv_file_path):
                    error_message = f"CSV file {csv_file_path} not found."
                    self.logger.error(error_message)
                    raise CSVFileNotFoundError(error_message)

                # Read CSV file
                try:
                    data = pd.read_csv(csv_file_path)
                except Exception as e:
                    error_message = f"Failed to read {csv_file_path}: {e}"
                    self.logger.error(error_message)
                    raise CSVReadError(error_message) from e

                # Clear existing content in the sheet tab
                try:
                    self.clear_sheet(sheet_id, tab_name)
                except Exception:
                    # The clear_sheet method already logs the error and raises SheetClearError
                    raise

                # Write new data to the sheet tab
                try:
                    self.write_data_to_sheet(sheet_id, tab_name, data)
                except Exception:
                    # The write_data_to_sheet method already logs the error and raises SheetWriteError
                    raise

                self.logger.info(f"Uploaded {csv_file} to {tab_name} in Google Sheet {sheet_id}\n")
