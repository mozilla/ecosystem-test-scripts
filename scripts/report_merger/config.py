# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""Configuration handling for the Report Merger."""

import json
import logging
from configparser import NoSectionError, NoOptionError
from json import JSONDecodeError


from pydantic import BaseModel, ValidationError, Field

from scripts.common.config import BaseConfig, InvalidConfigError, DIRECTORY_PATTERN


class ReportMergerConfig(BaseModel):
    """Model for Report Merger configuration."""

    reports_dir: str = Field(..., pattern=DIRECTORY_PATTERN)
    merged_reports_dir: str = Field(..., pattern=DIRECTORY_PATTERN)
    mappings: dict[str, list[str]]


class Config(BaseConfig):
    """Configuration handler for the Report Merger."""

    logger = logging.getLogger(__name__)

    def __init__(self, config_file: str = "config.ini") -> None:
        """Initialize the Config.

        Args:
            config_file (str): Path to the configuration file.

        Raises:
            InvalidConfigError: If the configuration file contains missing or invalid values,
                                or if an error occurs while building Metric Reporter arguments.
        """
        super().__init__(config_file)
        self.metric_reporter_config: ReportMergerConfig = self._parse_report_merger_config()
        self.logger.info("Successfully loaded configuration")

    def _parse_report_merger_config(self) -> ReportMergerConfig:
        try:
            return ReportMergerConfig(
                reports_dir=self.config_parser.get("report_merger", "reports_dir"),
                merged_reports_dir=self.config_parser.get("report_merger", "merged_reports_dir"),
                mappings=json.loads(self.config_parser.get("report_merger", "mappings")),
            )
        except (NoSectionError, NoOptionError, JSONDecodeError, ValidationError) as error:
            error_mapping: dict[type, str] = {
                NoSectionError: "The 'report_merger' section is missing",
                NoOptionError: "Missing config option in 'report_merger' section",
                JSONDecodeError: "Invalid JSON format in 'report_merger.mappings' section",
                ValidationError: "Unexpected value or schema in 'report_merger' section",
            }
            error_msg: str = next(m for t, m in error_mapping.items() if isinstance(error, t))
            self.logger.error(error_msg, exc_info=error)
            raise InvalidConfigError(error_msg) from error
