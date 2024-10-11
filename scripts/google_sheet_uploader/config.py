"""Configuration parser for the Google Sheet Uploader."""

import json
from configparser import ConfigParser, ExtendedInterpolation
from scripts.common.config import InvalidConfigError
from pydantic import BaseModel
from typing import List


class TabMapping(BaseModel):
    """Represents a mapping between a CSV file and a Google Sheets tab.

    Attributes:
        file_name (str): Name of the CSV file to upload.
        tab_name (str): Name of the Google Sheets tab.
    """

    file_name: str
    tab_name: str


class SheetMapping(BaseModel):
    """Associates a Google Sheets ID with multiple tab mappings.

    Attributes:
        sheet_id (str): The ID of the Google Sheet.
        tabs (List[TabMapping]): A list of tab mappings associated with the sheet.
    """

    sheet_id: str
    tabs: List[TabMapping]


class GoogleSheetUploaderConfig(BaseModel):
    """Encapsulates the entire configuration for the Google Sheet Uploader.

    Attributes:
        reports_dir (str): Directory where reports are stored.
        service_account_file (str): Path to the Google service account JSON file.
        mappings (List[SheetMapping]): List of sheet mappings.
    """

    reports_dir: str
    service_account_file: str
    mappings: List[SheetMapping]


class Config:
    """Configuration class for the Google Sheet Uploader.

    This class parses the `config.ini` file and provides configuration data
    for the uploader.

    Args:
        config_file (str): Path to the configuration file.
    """

    def __init__(self, config_file: str = "config.ini"):
        config_parser = ConfigParser(interpolation=ExtendedInterpolation())
        read_files = config_parser.read(config_file)
        if not read_files:
            raise FileNotFoundError(f"Configuration file '{config_file}' not found.")

        try:
            uploader_config = config_parser["google_sheet_uploader"]
        except KeyError:
            raise KeyError("Missing 'google_sheet_uploader' section in config.ini.")

        # Parse mappings
        mappings_str = uploader_config.get("mappings", "[]").strip().strip(";")
        try:
            mappings = json.loads(mappings_str)
        except json.JSONDecodeError as e:
            raise InvalidConfigError(f"Error parsing 'mappings' JSON: {e}")

        # Parse the entire configuration into Pydantic model
        config_data = {
            "reports_dir": uploader_config.get("reports_dir", "reports"),
            "service_account_file": uploader_config.get("service_account_file"),
            "mappings": mappings,
        }

        try:
            self.config = GoogleSheetUploaderConfig(**config_data)
        except InvalidConfigError as e:
            raise InvalidConfigError(f"Configuration validation error: {e}")

    @property
    def reports_dir(self) -> str:
        """Get the service account file path.

        Returns:
            str: Path to the Google service account JSON file.
        """
        return self.config.reports_dir

    @property
    def service_account_file(self) -> str:
        """Get the service account file path.

        Returns:
            str: Path to the Google service account JSON file.
        """
        return self.config.service_account_file

    @property
    def mappings(self) -> List[SheetMapping]:
        """Get the list of sheet mappings.

        Returns:
            List[SheetMapping]: List of sheet mappings.
        """
        return self.config.mappings
