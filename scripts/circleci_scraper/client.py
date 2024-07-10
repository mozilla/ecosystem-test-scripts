# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""CircleCIClient and related objects"""

import logging
from typing import Any, Type, TypeVar

import requests
from pydantic import BaseModel, ValidationError
from requests.exceptions import RequestException

from scripts.circleci_scraper.config import CircleCIScraperConfig
from scripts.circleci_scraper.error import BaseError

T = TypeVar("T", bound=BaseModel)


class VersionControlSystem(BaseModel):
    """CircleCI VCS."""

    branch: str | None = None
    commit: dict[str, Any] | None = None
    origin_repository_url: str | None = None
    provider_name: str | None = None
    review_id: str | None = None
    revision: str | None = None
    target_repository_url: str | None = None


class Pipeline(BaseModel):
    """CircleCI Pipeline."""

    created_at: str | None
    errors: list[Any]
    id: str
    number: int
    project_slug: str
    state: str
    trigger: dict[str, Any]
    updated_at: str | None = None
    vcs: VersionControlSystem | None = None


class PipelineGroup(BaseModel):
    """CircleCI Pipeline collection."""

    next_page_token: str | None = None
    items: list[Pipeline]


class Workflow(BaseModel):
    """CircleCI Workflow."""

    created_at: str | None
    id: str
    name: str
    pipeline_id: str
    pipeline_number: int
    project_slug: str
    started_by: str
    status: str
    stopped_at: str | None = None


class WorkflowGroup(BaseModel):
    """CircleCI Workflow collection."""

    next_page_token: str | None = None
    items: list[Workflow]


class Job(BaseModel):
    """CircleCI Job."""

    dependencies: list[Any]
    id: str
    job_number: int | None = None
    name: str
    project_slug: str
    started_at: str | None
    status: str
    stopped_at: str | None = None
    type: str


class JobGroup(BaseModel):
    """CircleCI Job collection."""

    next_page_token: str | None = None
    items: list[Job]


class TestMetadata(BaseModel):
    """CircleCI TestMetadata."""

    classname: str
    name: str
    result: str
    message: str
    run_time: float
    source: str


class TestMetadataGroup(BaseModel):
    """CircleCI TestMetadata collection."""

    next_page_token: str | None = None
    items: list[TestMetadata]


class Artifact(BaseModel):
    """CircleCI Artifact."""

    path: str
    node_index: int | None = None
    url: str


class ArtifactGroup(BaseModel):
    """CircleCI Artifact collection."""

    next_page_token: str | None = None
    items: list[Artifact]


class CircleCIClientError(BaseError):
    """Custom exception class for CircleCIClient errors."""

    pass


class CircleCIClient:
    """Client to interact with the CircleCI API."""

    logger = logging.getLogger(__name__)

    def __init__(self, circleci_scraper_config: CircleCIScraperConfig):
        """Initialize the CircleCIClient.

        Args:
            circleci_scraper_config (CircleCIScraperConfig): The CircleCI config information.
        """
        self._token: str = circleci_scraper_config.token
        self._vcs_slug: str = circleci_scraper_config.vcs_slug
        self._base_url: str = circleci_scraper_config.base_url

    def _headers(self) -> dict[str, str]:
        return {"Circle-Token": self._token, "Accept": "application/json"}

    def _make_request(
        self, endpoint: str, response_model: Type[T], params: dict[str, Any] | None = None
    ) -> T:
        url = f"{self._base_url}/{endpoint}"
        self.logger.info(f"Making API request to {url} with params {params}")
        try:
            response: requests.Response = requests.get(
                url, headers=self._headers(), params=params, timeout=10
            )
            response.raise_for_status()
            response_json: dict[str, Any] = response.json()
            return response_model(**response_json)
        except (RequestException, ValidationError) as error:
            if isinstance(error, RequestException):
                error_msg = f"Request to {url} failed"
            else:  # isinstance(error, ValidationError)
                error_msg = f"Unexpected schema for '{endpoint}' endpoint"
            self.logger.error(error_msg, exc_info=error)
            raise CircleCIClientError(error_msg, error)

    def get_pipelines(
        self, organization: str, next_page_token: str | None = None
    ) -> PipelineGroup:
        """Retrieve pipelines for the specified organization.

        Args:
            organization (str): The organization name.
            next_page_token (str | None): The token for the next page of results. Defaults to None.

        Returns:
            PipelineGroup: The response from the API as a Pipelines object.

        Raises:
            CircleCIClientError: If the request to the API fails.
        """
        endpoint = (
            f"pipeline?org-slug={self._vcs_slug}/{organization}"
            f"{(f'&page-token={next_page_token}' if next_page_token else '')}"
        )
        return self._make_request(endpoint, PipelineGroup)

    def get_workflows(self, pipeline_id: str, next_page_token: str | None = None) -> WorkflowGroup:
        """Retrieve workflows for the specified pipeline.

        Args:
            pipeline_id (str): The pipeline ID.
            next_page_token (str | None): The token for the next page of results. Defaults to None.

        Returns:
            WorkflowGroup: The response from the API.

        Raises:
            CircleCIClientError: If the request to the API fails.
        """
        endpoint = (
            f"pipeline/{pipeline_id}/workflow"
            f"{(f'?page-token={next_page_token}' if next_page_token else '')}"
        )
        return self._make_request(endpoint, WorkflowGroup)

    def get_jobs(self, workflow_id: str, next_page_token: str | None = None) -> JobGroup:
        """Retrieve jobs for the specified workflow.

        Args:
            workflow_id (str): The workflow ID.
            next_page_token (str | None): The token for the next page of results. Defaults to None.

        Returns:
            JobGroup: The response from the API.

        Raises:
            CircleCIClientError: If the request to the API fails.
        """
        endpoint = (
            f"workflow/{workflow_id}/job"
            f"{(f'?page-token={next_page_token}' if next_page_token else '')}"
        )
        return self._make_request(endpoint, JobGroup)

    def get_test_metadata(
        self,
        organization: str,
        repository: str,
        job_number: str,
        next_page_token: str | None = None,
    ) -> TestMetadataGroup:
        """Retrieve test metadata for the specified job.

        Args:
            organization (str): The organization name.
            repository (str): The repository name.
            job_number (str): The job number.
            next_page_token (str | None): The token for the next page of results. Defaults to None.

        Returns:
            TestMetadataGroup: The response from the API.

        Raises:
            CircleCIClientError: If the request to the API fails.
        """
        endpoint = (
            f"project/{self._vcs_slug}/{organization}/{repository}/{job_number}/tests"
            f"{(f'?page-token={next_page_token}' if next_page_token else '')}"
        )
        return self._make_request(endpoint, TestMetadataGroup)

    def get_job_artifacts(
        self,
        organization: str,
        repository: str,
        job_number: str,
        next_page_token: str | None = None,
    ) -> ArtifactGroup:
        """Retrieve job artifacts for the specified job.

        Args:
            organization (str): The organization name.
            repository (str): The repository name.
            job_number (str): The job number.
            next_page_token (str | None): The token for the next page of results. Defaults to None.

        Returns:
            ArtifactGroup: The response from the API.

        Raises:
            CircleCIClientError: If the request to the API fails.
        """
        endpoint = (
            f"project/{self._vcs_slug}/{organization}/{repository}/{job_number}/artifacts"
            f"{(f'?page-token={next_page_token}' if next_page_token else '')}"
        )
        return self._make_request(endpoint, ArtifactGroup)
