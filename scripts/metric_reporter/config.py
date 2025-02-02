# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""Configuration handling for the Metric Reporter."""

import logging
import re
from configparser import NoSectionError, NoOptionError
from pathlib import Path

from pydantic import BaseModel, ValidationError

from scripts.common.config import BaseConfig, InvalidConfigError


class MetricReporterArgs(BaseModel):
    """Model for Metric Reporter arguments."""

    repository: str
    workflow: str
    test_suite: str
    junit_artifact_path: Path
    coverage_artifact_path: Path


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

    @staticmethod
    def _normalize_name(name: str, delimiter: str = "") -> str:
        normalized = re.sub(r"[^a-zA-Z0-9_]+", delimiter, name).lower()
        return normalized.strip("_")

    def _build_metric_reporter_args(self) -> list[MetricReporterArgs]:
        # Here we assume that the structure of the test_result_dir directory is as follows:
        # test_result_dir/
        #     ├── repository/
        #         ├── workflow/
        #             ├── test_suite/
        #                 ├── metadata_dir/
        #                 ├── junit_artifact_dir/
        #                 ├── coverage_artifact_dir/
        try:
            test_metric_args_list: list[MetricReporterArgs] = []
            test_result_path = Path(self.common_config.test_result_dir)
            for directory_path, directory_names, files in test_result_path.walk():
                for directory_name in directory_names:
                    current_path = Path(directory_path) / directory_name
                    junit_artifact_path = current_path / self.common_config.junit_artifact_dir
                    coverage_artifact_path = (
                        current_path / self.common_config.coverage_artifact_dir
                    )
                    if junit_artifact_path.exists() or coverage_artifact_path.exists():
                        repository = self._normalize_name(Path(directory_path).parents[0].name)
                        test_suite = self._normalize_name(directory_name, "_")
                        test_metric_args = MetricReporterArgs(
                            repository=repository,
                            workflow=directory_path.name,
                            test_suite=test_suite,
                            junit_artifact_path=junit_artifact_path,
                            coverage_artifact_path=coverage_artifact_path,
                        )
                        test_metric_args_list.append(test_metric_args)

            return test_metric_args_list
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
