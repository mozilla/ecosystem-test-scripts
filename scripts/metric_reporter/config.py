# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""Configuration handling for the Metric Reporter."""

import logging
from configparser import NoSectionError, NoOptionError
from pathlib import Path

from pydantic import BaseModel, ValidationError

from scripts.common.config import BaseConfig, InvalidConfigError


class MetricReporterArgs(BaseModel):
    """Model for Metric Reporter arguments."""

    coverage_artifact_paths: list[Path] = []
    junit_artifact_paths: list[Path] = []


class MetricReporterConfig(BaseModel):
    """Model for Metric Reporter configuration."""

    gcp_project_id: str
    bigquery_dataset_name: str
    bigquery_service_account_file: str
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
        self.metric_reporter_args: list[MetricReporterArgs] = self._build_metric_reporter_args()
        self.logger.info("Successfully loaded configuration")

    def _parse_metric_reporter_config(self) -> MetricReporterConfig:
        try:
            gcp_project_id: str = self.config_parser.get("metric_reporter", "gcp_project_id")
            bigquery_dataset_name: str = self.config_parser.get(
                "metric_reporter", "bigquery_dataset_name"
            )
            bigquery_service_account_file: str = self.config_parser.get(
                "metric_reporter", "bigquery_service_account_file"
            )
            update_bigquery: bool = self.config_parser.getboolean(
                "metric_reporter", "update_bigquery", fallback=False
            )
            return MetricReporterConfig(
                gcp_project_id=gcp_project_id,
                bigquery_dataset_name=bigquery_dataset_name,
                bigquery_service_account_file=bigquery_service_account_file,
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

    def _build_metric_reporter_args(self) -> list[MetricReporterArgs]:
        # Here we assume that the structure of the test_result_dir directory is as follows:
        # test_result_dir/
        #     ├── repository/
        #          ├── coverage_artifact_dir/
        #               ├── coverage-1.json
        #               ├── coverage-2.json
        #          ├── junit_artifact_dir/
        #               ├── junit-1.xml
        #               ├── junit-2.xml
        test_result_dir = self.common_config.test_result_dir
        coverage_artifact_dir = self.common_config.coverage_artifact_dir
        junit_artifact_dir = self.common_config.junit_artifact_dir
        try:
            test_result_path = Path(test_result_dir)
            return [
                MetricReporterArgs(
                    coverage_artifact_paths=list(
                        repository_directory.joinpath(coverage_artifact_dir).glob("*.json")
                    ),
                    junit_artifact_paths=list(
                        repository_directory.joinpath(junit_artifact_dir).glob("*.xml")
                    ),
                )
                for repository_directory in test_result_path.iterdir()
            ]
        except (OSError, ValidationError) as error:
            error_mapping: dict[type, str] = {
                OSError: "Filesystem error while building Metric Reporter arguments",
                ValidationError: (
                    "Unexpected value or schema while building Metric Reporter arguments"
                ),
            }
            error_msg: str = next(m for t, m in error_mapping.items() if isinstance(error, t))
            self.logger.error(error_msg, exc_info=error)
            raise InvalidConfigError(error_msg) from error
