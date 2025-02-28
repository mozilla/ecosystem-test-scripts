# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""Module defining the base for all parsing in the Metric Reporter."""

import re
from datetime import datetime, timezone

from pydantic import BaseModel

from scripts.metric_reporter.constants import DATETIME_FORMAT
from scripts.metric_reporter.error import BaseError

ARTIFACT_FILE_PATTERN = re.compile(
    r"(?P<job_number>\d+)__(?P<epoch>\d+)__(?P<repository>.+?)__(?P<workflow>.+?)__(?P<test_suite>.+?)__(.*)"
)


class ParserError(BaseError):
    """Custom exception for errors raised by a metric reporter parser."""

    pass


class ArtifactFile(BaseModel):
    """Represents data contained in an artifact file name."""

    name: str
    job_number: int
    epoch: int
    repository: str
    workflow: str
    test_suite: str

    @property
    def job_timestamp(self) -> str:
        """Timestamp for the artifact job."""
        return datetime.fromtimestamp(self.epoch, tz=timezone.utc).strftime(DATETIME_FORMAT)


class BaseParser:
    """Base class for parsers."""

    @staticmethod
    def _parse_artifact_file_name(name: str) -> ArtifactFile:
        if match := ARTIFACT_FILE_PATTERN.match(name):
            return ArtifactFile(
                name=name,
                job_number=int(match.group("job_number")),
                epoch=int(match.group("epoch")),
                repository=match.group("repository"),
                workflow=match.group("workflow"),
                test_suite=match.group("test_suite"),
            )
        else:
            raise ParserError(f"Unexpected file name format: {name}")
