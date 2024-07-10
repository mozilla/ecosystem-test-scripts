# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""CircleCIScraper configs and related objects"""

import configparser
import json
import logging
from datetime import datetime, timezone, timedelta
from typing import Any, Literal, cast

from pydantic import BaseModel, ValidationError, Field

from scripts.circleci_scraper.error import BaseError

DIRECTORY_PATTERN = r"^[^<>:;,?\"*|]+$"
REPOSITORY_PATTERN = r"^[a-zA-Z0-9-_]+$"
TOKEN_PATTERN = r"^\S+$"  # nosec B105
URL_PATTERN = r"^https?://[a-zA-Z0-9.-]+(/[a-zA-Z0-9._~-]*)*$"


class MainConfig(BaseModel):
    """Main Configuration."""

    test_result_dir: str = Field(..., pattern=DIRECTORY_PATTERN)
    test_metadata_dir: str = Field(..., pattern=DIRECTORY_PATTERN)
    test_artifact_dir: str = Field(..., pattern=DIRECTORY_PATTERN)


class CircleCIScraperPipelineConfig(BaseModel):
    """CircleCIScraper Config Pipelines."""

    organization: Literal["mozilla", "mozilla-services"]
    repository: str = Field(..., pattern=REPOSITORY_PATTERN)
    workflows: dict[str, list[str]]
    branches: list[str] | None = []


class CircleCIScraperConfig(BaseModel):
    """CircleCIScraper Config."""

    token: str = Field(..., pattern=TOKEN_PATTERN)
    base_url: str = Field(..., pattern=URL_PATTERN)
    vcs_slug: Literal["gh"]
    pipelines: list[CircleCIScraperPipelineConfig]
    days_of_data: int | None
    date_limit: datetime | None


class InvalidConfigError(BaseError):
    """Raise for errors in the CircleCIScraper configuration."""

    pass


class Config:
    """Load and validate the CircleCIScraper configuration."""

    logger = logging.getLogger(__name__)

    def __init__(self, config_file: str = "config.ini") -> None:
        """Initialize the configuration by reading and parsing the config file.

        Args:
            config_file (str): Path to the configuration file. Default is 'ecosystem-test-scripts/config.ini'.

        Raises:
            InvalidCircleCIScraperConfigError: If there's an error in the configuration.
        """
        config_parser = configparser.ConfigParser()
        config_parser.read(config_file)
        self.main_config: MainConfig = self._parse_main_config(config_parser)
        self.circleci_scraper_config: CircleCIScraperConfig = self._parse_circleci_scraper_config(
            config_parser
        )
        self.logger.info("Successfully loaded configuration")

    def _parse_main_config(self, config_parser: configparser.ConfigParser) -> MainConfig:
        try:
            return MainConfig(
                test_result_dir=config_parser.get("main", "test_result_dir"),
                test_metadata_dir=config_parser.get("main", "test_metadata_dir"),
                test_artifact_dir=config_parser.get("main", "test_artifact_dir"),
            )
        except (configparser.NoOptionError, ValidationError) as error:
            if isinstance(error, configparser.NoOptionError):
                error_msg = "Missing config option in 'main' section"
            else:  # isinstance(error, ValidationError)
                error_msg = "Unexpected value in 'main' section"
            self.logger.error(error_msg, exc_info=error)
            raise InvalidConfigError(error_msg, error)

    def _parse_circleci_scraper_config(
        self, config_parser: configparser.ConfigParser
    ) -> CircleCIScraperConfig:
        try:
            pipelines_json_str: str = config_parser.get("circleci_scraper", "pipelines")
            pipelines_json: Any = json.loads(pipelines_json_str)
            pipelines: list[CircleCIScraperPipelineConfig] = [
                CircleCIScraperPipelineConfig(**pipeline) for pipeline in pipelines_json
            ]
            days_of_data: int | None = config_parser.getint(
                "circleci_scraper", "days_of_data", fallback=None
            )
            date_limit: datetime | None = (
                datetime.now(timezone.utc) - timedelta(days=float(days_of_data))
                if days_of_data
                else None
            )
            return CircleCIScraperConfig(
                token=config_parser.get("circleci_scraper", "token"),
                base_url=config_parser.get("circleci_scraper", "base_url"),
                vcs_slug=cast(Literal["gh"], config_parser.get("circleci_scraper", "vcs_slug")),
                pipelines=pipelines,
                days_of_data=days_of_data,
                date_limit=date_limit,
            )
        except (configparser.NoOptionError, json.JSONDecodeError, ValidationError) as error:
            if isinstance(error, configparser.NoOptionError):
                error_msg = "Missing config option in 'circleci_scraper' section"
            elif isinstance(error, json.JSONDecodeError):
                error_msg = "Invalid JSON format in 'circleci_scraper.pipelines' section"
            else:  # isinstance(error, ValidationError)
                error_msg = "Unexpected value or schema in 'circleci_scraper' section"

            self.logger.error(error_msg, exc_info=error)
            raise InvalidConfigError(error_msg, error)
