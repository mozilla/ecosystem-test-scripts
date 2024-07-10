# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""CircleCIScraper and related objects"""

import json
import logging
import os
from datetime import datetime, timezone
from typing import Any

import requests
from requests.exceptions import RequestException

from client import (
    CircleCIClient,
    PipelineGroup,
    WorkflowGroup,
    JobGroup,
    Job,
    TestMetadataGroup,
    ArtifactGroup,
    Artifact,
    Workflow,
)
from config import CircleCIScraperPipelineConfig, MainConfig
from scripts.circleci_scraper.error import BaseError


class CircleCIScraperError(BaseError):
    """Custom exception class for CircleCIScraper errors."""

    pass


class CircleCIScraper:
    """Export CircleCI test metadata and artifacts."""

    logger = logging.getLogger(__name__)

    def __init__(self, main_config: MainConfig, client: CircleCIClient):
        """Initialize the CircleCIScraper.

        Args:
            main_config (MainConfig): Directory information to store test results.
            client (CircleCIClient): The CircleCI client to interact with the API.

        """
        self._client = client
        self._test_result_dir = main_config.test_result_dir
        self._test_metadata_dir = main_config.test_metadata_dir
        self._test_artifact_dir = main_config.test_artifact_dir

    def export_test_metadata_and_artifacts(
        self,
        pipeline_configs: list[CircleCIScraperPipelineConfig],
        date_limit: datetime | None = None,
    ) -> None:
        """Export test metadata and artifacts for a list of pipelines.

        Args:
            pipeline_configs (list[CircleCIScraperPipelineConfig]): A list of pipeline
                                                                    configurations.
            date_limit (datetime | None): The date limit for fetching data. Defaults to None.

        Raises:
            CircleCIClientError: If there is an error in the CircleCI API request.
            CircleCIScraperError: If there is an error in downloading the artifacts.
        """
        for pipeline_config in pipeline_configs:
            self.logger.info(f"Scrape {pipeline_config.organization}/{pipeline_config.repository}")
            self.export_test_metadata_and_artifacts_by_pipeline(pipeline_config, date_limit)

    def export_test_metadata_and_artifacts_by_pipeline(
        self, pipeline_config: CircleCIScraperPipelineConfig, date_limit: datetime | None = None
    ) -> None:
        """Export test metadata and artifacts for a single pipeline.

        Args:
            pipeline_config (CircleCIScraperPipelineConfig): A pipeline configuration.
            date_limit (datetime | None): The date limit for fetching data. Defaults to None.

        Raises:
            CircleCIClientError: If there is an error in the CircleCI API request.
            CircleCIScraperError: If there is an error in downloading the artifacts.
        """
        next_page_token: str | None = None
        while True:
            pipelines: PipelineGroup = self._client.get_pipelines(
                pipeline_config.organization, next_page_token
            )
            for pipeline in pipelines.items:
                # Filter for branches, usually we only observe 'main' or equivalent
                if (
                    pipeline_config.branches
                    and pipeline.vcs
                    and pipeline.vcs.branch not in pipeline_config.branches
                ):
                    continue
                # Filter for date limit
                created_at_datetime = datetime.strptime(
                    pipeline.created_at, "%Y-%m-%dT%H:%M:%S.%fZ"
                ).replace(tzinfo=timezone.utc)
                if date_limit and created_at_datetime < date_limit:
                    return
                self.export_test_metadata_and_artifacts_by_pipeline_id(
                    pipeline.id,
                    pipeline_config.organization,
                    pipeline_config.repository,
                    pipeline_config.workflows,
                )
            next_page_token = pipelines.next_page_token
            if not next_page_token:
                break

    def export_test_metadata_and_artifacts_by_pipeline_id(
        self,
        pipeline_id: str,
        organization: str,
        repository: str,
        workflow_configs: dict[str, list[str]],
    ) -> None:
        """Export test metadata and artifacts for a specific pipeline ID.

        Args:
            pipeline_id (str): The pipeline ID.
            organization (str): The organization name.
            repository (str): The repository name.
            workflow_configs (dict[str, list[str]]): The workflow configurations.

        Raises:
            CircleCIClientError: If there is an error in the CircleCI API request.
            CircleCIScraperError: If there is an error in downloading the artifacts.
        """
        next_page_token: str | None = None
        while True:
            workflows: WorkflowGroup = self._client.get_workflows(pipeline_id, next_page_token)
            for workflow in workflows.items:
                if workflow.name in workflow_configs:
                    job_names = workflow_configs[workflow.name]
                    self.export_test_metadata_and_artifacts_workflow_id(
                        organization, repository, workflow, job_names
                    )
            next_page_token = workflows.next_page_token
            if not next_page_token:
                break

    def export_test_metadata_and_artifacts_workflow_id(
        self,
        organization: str,
        repository: str,
        workflow: Workflow,
        job_names: list[str],
    ) -> None:
        """Export test metadata and artifacts for a specific workflow ID.

        Args:
            organization (str): The organization name.
            repository (str): The repository name.
            workflow (Workflow): The workflow.
            job_names (list[str]): A list of job names.

        Raises:
            CircleCIClientError: If there is an error in the CircleCI API request.
            CircleCIScraperError: If there is an error in downloading the artifacts.
        """
        next_page_token: str | None = None
        while True:
            jobs: JobGroup = self._client.get_jobs(workflow.id, next_page_token)
            for job in jobs.items:
                if job.name in job_names:
                    self.export_test_metadata_by_job(organization, repository, workflow.name, job)
                    self.export_test_artifacts_by_job(organization, repository, workflow.name, job)
            next_page_token = jobs.next_page_token
            if not next_page_token:
                break

    def export_test_metadata_by_job(
        self,
        organization: str,
        repository: str,
        workflow_name: str,
        job: Job,
    ) -> None:
        """Export test metadata for a specific job.

        Args:
            organization (str): The organization name.
            repository (str): The repository name.
            workflow_name (str): The workflow name.
            job (Job): The job details.

        Raises:
            CircleCIClientError: If there is an error in the CircleCI API request.
            CircleCIScraperError: If there is an error in downloading the artifacts.
        """
        file_content: dict[str, Any] = {"job": job.dict(), "test_metadata": []}
        next_page_token: str | None = None
        while True:
            test_metadata: TestMetadataGroup = self._client.get_test_metadata(
                organization, repository, str(job.job_number), next_page_token
            )
            if not test_metadata:
                break
            file_content["test_metadata"] += [item.dict() for item in test_metadata.items]
            next_page_token = test_metadata.next_page_token
            if not next_page_token:
                break
        if not file_content["test_metadata"]:
            self.logger.info(f"There is no test metadata for job {str(job.job_number)}")
            return
        self.export_test_metadata(repository, workflow_name, job, file_content)

    def export_test_metadata(
        self, repository: str, workflow_name: str, job: Job, file_content: dict[str, Any]
    ):
        """Export test metadata.

        Args:
            repository (str): The repository name.
            workflow_name (str): The workflow name.
            job (Job): The job details.
            file_content (Dict[str, Any]): The content to be output.

        Raises:
            CircleCIClientError: If there is an error in the CircleCI API request.
            CircleCIScraperError: If there is an error in downloading the artifacts.
        """
        test_metadata_directory: str = os.path.join(
            self._test_result_dir, repository, workflow_name, job.name, self._test_metadata_dir
        )
        if not os.path.isdir(test_metadata_directory):
            os.makedirs(test_metadata_directory)
        file_path: str = os.path.join(test_metadata_directory, f"{job.job_number}.json")
        if os.path.exists(file_path):
            self.logger.info(f"{file_path} already exists, skipping download.")
        else:
            with open(file_path, "w") as file:
                file.write(json.dumps(file_content, default=str))
            self.logger.info(f"Output {file_path}")

    def export_test_artifacts_by_job(
        self,
        organization: str,
        repository: str,
        workflow_name: str,
        job: Job,
    ) -> None:
        """Export test artifacts for a specific job.

        Args:
            organization (str): The organization name.
            repository (str): The repository name.
            workflow_name (str): The workflow name.
            job (Job): The job details.

        Raises:
            CircleCIClientError: If there is an error in the CircleCI API request.
            CircleCIScraperError: If there is an error in downloading the artifacts.
        """
        test_artifacts: list[Artifact] = []
        next_page_token: str | None = None
        while True:
            artifacts: ArtifactGroup = self._client.get_job_artifacts(
                organization, repository, str(job.job_number), next_page_token
            )
            if not artifacts:
                break
            test_artifacts += [item for item in artifacts.items if item.path.endswith(".xml")]
            next_page_token = artifacts.next_page_token
            if not next_page_token:
                break
        self.export_test_artifacts(repository, workflow_name, job, test_artifacts)

    def export_test_artifacts(
        self, repository: str, workflow_name: str, job: Job, artifacts: list[Artifact]
    ):
        """Export a given list of test artifacts.

        Args:
            repository (str): The repository name.
            workflow_name (str): The workflow name.
            job (Job): The job details.
            artifacts (list[Artifact]): The list of artifacts.

        Raises:
            CircleCIClientError: If there is an error in the CircleCI API request.
            CircleCIScraperError: If there is an error in downloading the artifacts.
        """
        artifact_directory: str = os.path.join(
            self._test_result_dir,
            repository,
            workflow_name,
            job.name,
            self._test_artifact_dir,
            str(job.job_number),
        )
        if artifacts and not os.path.isdir(artifact_directory):
            os.makedirs(artifact_directory)
        for index, artifact in enumerate(artifacts):
            # adding the index prefix guarantees file name uniqueness
            file_path: str = os.path.join(
                artifact_directory, f"{index}-{os.path.basename(artifact.path)}"
            )
            if os.path.exists(file_path):
                self.logger.info(f"{file_path} already exists, skipping download.")
            else:
                self.download_artifact(file_path, artifact.url)

    def download_artifact(self, file_name: str, url: str) -> None:
        """Download an artifact from the specified URL.

        Args:
            file_name (str): The name of the destination file.
            url (str): The URL of the artifact to download.

        Raises:
            CircleCIScraperError: If there is an error in downloading the artifact.
        """
        try:
            response: requests.Response = requests.get(url, timeout=10)
            response.raise_for_status()
            with open(file_name, "wb") as file:
                file.write(response.content)
            self.logger.info(f"Output {file_name}")
        except RequestException as error:
            self.logger.error(f"Failed to download artifact from {url}", exc_info=error)
            raise CircleCIScraperError(f"Failed to download artifact from {url}", error)
