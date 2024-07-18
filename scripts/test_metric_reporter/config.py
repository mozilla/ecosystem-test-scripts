# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""Configuration handling for the Test Metric Reporter."""

import logging
import re
from configparser import ConfigParser, NoSectionError, NoOptionError
from pathlib import Path

from pydantic import BaseModel, ValidationError, Field

from scripts.common.config import BaseConfig, InvalidConfigError, DIRECTORY_PATTERN


class TestMetricArgs(BaseModel):
    """Model for test metric arguments."""

    test_metadata_directory_path: str
    csv_report_file_path: str


class TestMetricReporterConfig(BaseModel):
    """Model for test metric reporter configuration."""

    reports_dir: str = Field(..., pattern=DIRECTORY_PATTERN)


class Config(BaseConfig):
    """Configuration handler for the Test Metric Reporter."""

    logger = logging.getLogger(__name__)

    def __init__(self, config_file: str = "config.ini") -> None:
        """Initialize the Config.

        Args:
            config_file (str): Path to the configuration file.

        Raises:
            InvalidConfigError: If the configuration file contains missing or invalid values,
                                or if an error occurs while building test metric reporter arguments.
        """
        super().__init__(config_file)
        self.test_metric_reporter_config: TestMetricReporterConfig = (
            self._parse_test_metric_reporter_config(self.config_parser)
        )
        self.test_metric_reporter_args: list[TestMetricArgs] = (
            self._build_test_metric_reporter_args()
        )
        self.logger.info("Successfully loaded configuration")

    def _parse_test_metric_reporter_config(
        self, config_parser: ConfigParser
    ) -> TestMetricReporterConfig:
        try:
            reports_dir: str = config_parser.get("test_metric_reporter", "reports_dir")
            return TestMetricReporterConfig(reports_dir=reports_dir)
        except (NoSectionError, NoOptionError, ValidationError) as error:
            error_mapping: dict[type, str] = {
                NoSectionError: "The 'test_metric_reporter' section is missing",
                NoOptionError: "Missing config option in 'test_metric_reporter' section",
                ValidationError: "Unexpected value or schema in 'test_metric_reporter' section",
            }
            error_msg: str = error_mapping[type(error)]
            self.logger.error(error_msg, exc_info=error)
            raise InvalidConfigError(error_msg, error)

    @staticmethod
    def _normalize_name(name: str, delimiter: str = "") -> str:
        normalized = re.sub(r"[^a-zA-Z0-9_]+", delimiter, name).lower()
        return normalized.strip("_")

    def _build_test_metric_reporter_args(self) -> list[TestMetricArgs]:
        # Here we assume that the structure of the test_result_dir directory is as follows:
        # test_result_dir/
        #     ├── repository/
        #         ├── workflow/
        #             ├── test_suite/
        #                 ├── test_metadata_dir/
        try:
            test_metric_args_list: list[TestMetricArgs] = []
            test_result_dir_path = Path(self.common_config.test_result_dir)
            for directory_path, directory_names, _ in test_result_dir_path.walk():
                for directory_name in directory_names:
                    current_path = Path(directory_path) / directory_name
                    if current_path.name == self.common_config.test_metadata_dir:
                        parts: tuple[str, ...] = current_path.parts
                        repository_name: str = parts[-4]
                        test_suite_name: str = parts[-2]
                        csv_report_file_name = (
                            f"{self._normalize_name(repository_name)}_"
                            f"{self._normalize_name(test_suite_name, '_')}_"
                            f"results.csv"
                        )
                        test_metric_args = TestMetricArgs(
                            test_metadata_directory_path=str(current_path),
                            csv_report_file_path=str(
                                Path(self.test_metric_reporter_config.reports_dir)
                                / csv_report_file_name
                            ),
                        )
                        test_metric_args_list.append(test_metric_args)

            return test_metric_args_list
        except (OSError, ValidationError) as error:
            error_mapping: dict[type, str] = {
                OSError: "Filesystem error while building test metric reporter arguments",
                ValidationError: (
                    "Unexpected value or schema while building test metric reporter arguments"
                ),
            }
            error_msg: str = error_mapping[type(error)]
            self.logger.error(error_msg, exc_info=error)
            raise InvalidConfigError(error_msg, error)
