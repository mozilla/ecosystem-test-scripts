# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""Configuration handling for the Metric Reporter."""

import logging
from configparser import NoSectionError, NoOptionError

from pydantic import BaseModel, ValidationError

from scripts.common.config import BaseConfig, InvalidConfigError


class MetricReporterConfig(BaseModel):
    """Model for Metric Reporter configuration."""

    service_account_file: str
    bigquery_dataset_name: str
    update_bigquery: bool = False


class Config(BaseConfig):
    """Configuration handler for the Metric Reporter."""

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
        self.metric_reporter_config: MetricReporterConfig = self._parse_metric_reporter_config()
        self.logger.info("Successfully loaded configuration")

    def _parse_metric_reporter_config(self) -> MetricReporterConfig:
        try:
            service_account_file: str = self.config_parser.get(
                "metric_reporter", "service_account_file"
            )
            bigquery_dataset_name: str = self.config_parser.get(
                "metric_reporter", "bigquery_dataset_name"
            )
            update_bigquery: bool = self.config_parser.getboolean(
                "metric_reporter", "update_bigquery", fallback=False
            )
            return MetricReporterConfig(
                service_account_file=service_account_file,
                bigquery_dataset_name=bigquery_dataset_name,
                update_bigquery=update_bigquery,
            )
        except (NoSectionError, NoOptionError, ValidationError) as error:
            error_mapping: dict[type, str] = {
                NoSectionError: "The 'metric_reporter' section is missing",
                NoOptionError: "Missing config option in 'metric_reporter' section",
                ValidationError: "Unexpected value or schema in 'metric_reporter' section",
            }
            error_msg: str = next(m for t, m in error_mapping.items() if isinstance(error, t))
            self.logger.error(error_msg, exc_info=error)
            raise InvalidConfigError(error_msg) from error
