import os
import pandas as pd
from googleapiclient.discovery import build
from google.oauth2 import service_account
import logging

class GoogleSheetUploader:
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)

        self.credentials = service_account.Credentials.from_service_account_file(
            self.config.service_account_file,
            scopes=['https://www.googleapis.com/auth/spreadsheets']
        )
        self.service = build('sheets', 'v4', credentials=self.credentials)

    def clear_sheet(self, sheet_id, tab_name):
        sheet = self.service.spreadsheets()
        batch_clear_values_request_body = {
            'ranges': [tab_name]
        }
        request = sheet.values().batchClear(
            spreadsheetId=sheet_id,
            body=batch_clear_values_request_body
        )
        response = request.execute()
        return response

    def write_data_to_sheet(self, sheet_id, tab_name, data):
        sheet = self.service.spreadsheets()
        data = data.fillna('')
        values = [data.columns.values.tolist()] + data.values.tolist()
        body = {
            'values': values
        }
        result = sheet.values().update(
            spreadsheetId=sheet_id,
            range=tab_name,
            valueInputOption='RAW',
            body=body
        ).execute()
        return result

    def process_csv_files(self):
        for mapping in self.config.mappings:
            csv_file = mapping['file_name']
            sheet_id = mapping['sheet_id']
            tab_name = mapping['tab_name']

            self.logger.info(f"Processing {csv_file} -> Sheet ID: {sheet_id}, Tab: {tab_name}")

            # Adjust the path to your CSV files if necessary
            csv_file_path = os.path.join('reports', csv_file)

            # Check if the CSV file exists
            if not os.path.exists(csv_file_path):
                self.logger.error(f"CSV file {csv_file_path} not found.")
                continue

            # Read CSV file
            try:
                data = pd.read_csv(csv_file_path)
            except Exception as e:
                self.logger.error(f"Failed to read {csv_file_path}: {e}")
                continue

            # Clear existing content in the sheet tab
            try:
                self.clear_sheet(sheet_id, tab_name)
            except Exception as e:
                self.logger.error(f"Failed to clear sheet {sheet_id}, tab {tab_name}: {e}")
                continue

            # Write new data to the sheet tab
            try:
                self.write_data_to_sheet(sheet_id, tab_name, data)
            except Exception as e:
                self.logger.error(f"Failed to write data to sheet {sheet_id}, tab {tab_name}: {e}")
                continue

            self.logger.info(f"Uploaded {csv_file} to {tab_name} in Google Sheet {sheet_id}\n")
