# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""CircleCIScraper configs and related objects"""

import json
import logging
from configparser import ConfigParser, NoSectionError, NoOptionError
from datetime import datetime, timezone, timedelta
from typing import Any, Literal, cast

from pydantic import BaseModel, ValidationError, Field

from scripts.common.config import BaseConfig, InvalidConfigError

REPOSITORY_PATTERN = r"^[a-zA-Z0-9-_]+$"
TOKEN_PATTERN = r"^\S+$"  # nosec B105
URL_PATTERN = r"^https?://[a-zA-Z0-9.-]+(/[a-zA-Z0-9._~-]*)*$"


class CircleCIScraperJobConfig(BaseModel):
    """CircleCIScraper Config Job."""

    job_name: str
    test_suite: str


class CircleCIScraperPipelineConfig(BaseModel):
    """CircleCIScraper Config Pipelines."""

    organization: Literal["mozilla", "mozilla-services"]
    repository: str = Field(..., pattern=REPOSITORY_PATTERN)
    workflows: dict[str, list[CircleCIScraperJobConfig]]
    branches: list[str] | None = []


class CircleCIScraperConfig(BaseModel):
    """CircleCIScraper Config."""

    token: str = Field(..., pattern=TOKEN_PATTERN)
    service_account_file: str
    base_url: str = Field(..., pattern=URL_PATTERN)
    vcs_slug: Literal["gh"]
    pipelines: list[CircleCIScraperPipelineConfig]
    days_of_data: int | None
    date_limit: datetime | None


class Config(BaseConfig):
    """Load and validate the CircleCIScraper configuration."""

    logger = logging.getLogger(__name__)

    def __init__(self, config_file: str = "config.ini") -> None:
        """Initialize the configuration by reading and parsing the config file.

        Args:
            config_file (str): Path to the configuration file. Default is 'ecosystem-test-scripts/config.ini'.

        Raises:
            InvalidCircleCIScraperConfigError: If there's an error in the configuration.
        """
        super().__init__(config_file)
        self.circleci_scraper_config: CircleCIScraperConfig = self._parse_circleci_scraper_config(
            self.config_parser
        )
        self.logger.info("Successfully loaded configuration")

    def _parse_circleci_scraper_config(self, config_parser: ConfigParser) -> CircleCIScraperConfig:
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
                service_account_file=config_parser.get("circleci_scraper", "service_account_file"),
                base_url=config_parser.get("circleci_scraper", "base_url"),
                vcs_slug=cast(Literal["gh"], config_parser.get("circleci_scraper", "vcs_slug")),
                pipelines=pipelines,
                days_of_data=days_of_data,
                date_limit=date_limit,
            )
        except (NoSectionError, NoOptionError, json.JSONDecodeError, ValidationError) as error:
            error_mapping: dict[type, str] = {
                NoSectionError: "The 'circleci_scraper' section is missing",
                NoOptionError: "Missing config option in 'circleci_scraper' section",
                json.JSONDecodeError: "Invalid JSON format in 'circleci_scraper.pipelines' section",
                ValidationError: "Unexpected value or schema in 'circleci_scraper' section",
            }
            error_msg: str = next(m for t, m in error_mapping.items() if isinstance(error, t))
            self.logger.error(error_msg, exc_info=error)
            raise InvalidConfigError(error_msg) from error
