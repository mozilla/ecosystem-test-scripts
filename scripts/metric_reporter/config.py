# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""Configuration handling for the Metric Reporter."""

import logging
from configparser import ConfigParser, NoSectionError, NoOptionError

from pydantic import BaseModel, Field, ValidationError

from scripts.metric_reporter.error import BaseError

DIRECTORY_PATTERN = r"^[^<>:;,?\"*|]+$"


class MetricReporterConfig(BaseModel):
    """Model for Metric Reporter configuration."""

    gcp_project_id: str
    test_result_bucket: str
    junit_artifact_dir: str = Field(..., pattern=DIRECTORY_PATTERN)
    coverage_artifact_dir: str = Field(..., pattern=DIRECTORY_PATTERN)
    service_account_file: str
    bigquery_dataset_name: str
    update_bigquery: bool = False


class InvalidConfigError(BaseError):
    """Custom error raised for invalid configurations."""

    pass


class Config:
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
        self.config_parser = ConfigParser()
        self.config_parser.read(config_file)
        self.metric_reporter_config: MetricReporterConfig = self._parse_metric_reporter_config(
            self.config_parser
        )
        self.logger.info("Successfully loaded configuration")

    def _parse_metric_reporter_config(self, config_parser: ConfigParser) -> MetricReporterConfig:
        try:
            return MetricReporterConfig(
                gcp_project_id=config_parser.get("metric_reporter", "gcp_project_id"),
                test_result_bucket=config_parser.get("metric_reporter", "test_result_bucket"),
                junit_artifact_dir=config_parser.get("metric_reporter", "junit_artifact_dir"),
                coverage_artifact_dir=config_parser.get(
                    "metric_reporter", "coverage_artifact_dir"
                ),
                service_account_file=config_parser.get("metric_reporter", "service_account_file"),
                bigquery_dataset_name=config_parser.get(
                    "metric_reporter", "bigquery_dataset_name"
                ),
                update_bigquery=config_parser.getboolean(
                    "metric_reporter", "update_bigquery", fallback=False
                ),
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
