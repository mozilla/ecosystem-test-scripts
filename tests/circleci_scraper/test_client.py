# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""Tests for the CircleCIClient."""

import pytest
from requests.exceptions import HTTPError, ConnectionError, Timeout
from scripts.circleci_scraper.client import CircleCIClient, CircleCIClientError
from scripts.circleci_scraper.config import (
    CircleCIScraperConfig,
    CircleCIScraperJobConfig,
    CircleCIScraperPipelineConfig,
)


@pytest.mark.parametrize(
    "exception",
    [
        HTTPError("HTTP Error occurred"),
        ConnectionError("Connection Error occurred"),
        Timeout("Timeout occurred"),
    ],
)
def test_get_pipelines_request_error(mocker, exception):
    """Test the CircleCIClient get_pipelines method with various types of RequestError.

    Args:
        exception (RequestError): A type of RequestError.
    """
    config = CircleCIScraperConfig(
        token="token",  # nosec B106
        vcs_slug="gh",
        base_url="https://fake.api",
        pipelines=[
            CircleCIScraperPipelineConfig(
                organization="mozilla",
                repository="repo",
                workflows={
                    "workflow": [CircleCIScraperJobConfig(job_name="job", test_suite="suite")]
                },
            )
        ],
        days_of_data=30,
        date_limit="2024-01-01",
    )
    client = CircleCIClient(circleci_scraper_config=config)
    expected_message = "Request to https://fake.api/pipeline?org-slug=gh/mozilla failed"
    mocker.patch("requests.get", side_effect=exception)

    with pytest.raises(CircleCIClientError) as actual_error:
        client.get_pipelines(organization=config.pipelines[0].organization)

    assert expected_message in str(actual_error.value)
    assert isinstance(actual_error.value.__cause__, type(exception))
