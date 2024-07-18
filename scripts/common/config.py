# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""Configuration handling for the ecosystem test scripts."""

import logging
from configparser import ConfigParser, NoSectionError, NoOptionError

from pydantic import BaseModel, ValidationError, Field

from scripts.common.error import BaseError

# Constants
DIRECTORY_PATTERN = r"^[^<>:;,?\"*|]+$"


class CommonConfig(BaseModel):
    """Configuration model for common settings."""

    test_result_dir: str = Field(..., pattern=DIRECTORY_PATTERN)
    test_metadata_dir: str = Field(..., pattern=DIRECTORY_PATTERN)
    test_artifact_dir: str = Field(..., pattern=DIRECTORY_PATTERN)


class InvalidConfigError(BaseError):
    """Custom error raised for invalid configurations."""

    pass


class BaseConfig:
    """Base configuration handler for the ecosystem test scripts."""

    logger = logging.getLogger(__name__)

    def __init__(self, config_file: str = "config.ini") -> None:
        """Initialize the BaseConfig.

        Args:
            config_file (str): Path to the configuration file.

        Raises:
            InvalidConfigError: If the configuration file contains missing or invalid values.
        """
        self.config_parser = ConfigParser()
        self.config_parser.read(config_file)
        self.common_config: CommonConfig = self._parse_main_config(self.config_parser)

    def _parse_main_config(self, config_parser: ConfigParser) -> CommonConfig:
        try:
            return CommonConfig(
                test_result_dir=config_parser.get("common", "test_result_dir"),
                test_metadata_dir=config_parser.get("common", "test_metadata_dir"),
                test_artifact_dir=config_parser.get("common", "test_artifact_dir"),
            )
        except (NoSectionError, NoOptionError, ValidationError) as error:
            error_mapping: dict[type, str] = {
                NoSectionError: "The 'common' section is missing",
                NoOptionError: "Missing config option in 'common' section",
                ValidationError: "Unexpected value in 'common' section",
            }
            error_msg = error_mapping[type(error)]
            self.logger.error(error_msg, exc_info=error)
            raise InvalidConfigError(error_msg, error)
