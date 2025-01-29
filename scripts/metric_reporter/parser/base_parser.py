# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""Module defining the base for all parsing in the Metric Reporter."""

import re

from scripts.common.error import BaseError

JOB_DIRECTORY_PATTERN = re.compile(
    r"(?P<job_number>\d+)_(?P<job_timestamp>\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z)"
)


class ParserError(BaseError):
    """Custom exception for errors raised by a metric reporter parser."""

    pass
