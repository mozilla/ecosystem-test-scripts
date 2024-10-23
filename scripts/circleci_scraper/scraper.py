# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""CircleCIScraper and related objects"""

import json
import logging
import re
from pathlib import Path
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
from scripts.circleci_scraper.config import CircleCIScraperPipelineConfig
from scripts.common.config import CommonConfig
from scripts.common.error import BaseError

COVERAGE_FILE_REGEX = r".*cov.*\.json$"
CANCELED_JOB_STATUS = "canceled"
RUNNING_JOB_STATUS = "running"


class CircleCIScraperError(BaseError):
    """Custom exception class for CircleCIScraper errors."""

    pass


class CircleCIScraper:
    """Export CircleCI test metadata and artifacts."""

    logger = logging.getLogger(__name__)

    def __init__(self, common_config: CommonConfig, client: CircleCIClient):
        """Initialize the CircleCIScraper.

        Args:
            common_config (CommonConfig): Directory information to store test results.
            client (CircleCIClient): The CircleCI client to interact with the API.

        """
        self._client = client
        self._test_result_dir = common_config.test_result_dir
        self._test_metadata_dir = common_config.test_metadata_dir
        self._junit_artifact_dir = common_config.junit_artifact_dir
        self._coverage_artifact_dir = common_config.coverage_artifact_dir

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
                    if not job.job_number:
                        # This happens when workflows are cancelled before a number is assigned
                        # to the test job
                        logging.warning(
                            f"Skipping data for workflow {workflow.id} because the job number is "
                            f"missing for {organization}>{repository}>{workflow.name}>{job.name}"
                        )
                        continue
                    if job.status in [CANCELED_JOB_STATUS, RUNNING_JOB_STATUS]:
                        logging.warning(
                            f"Skipping data for workflow {workflow.id}, "
                            f"{organization}>{repository}>{workflow.name}>{job.name} because the"
                            " job is in progress or cancelled."
                        )
                        continue
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
        file_content: dict[str, Any] = {"job": job.model_dump(), "test_metadata": []}
        next_page_token: str | None = None
        while True:
            test_metadata: TestMetadataGroup = self._client.get_test_metadata(
                organization, repository, str(job.job_number), next_page_token
            )
            if not test_metadata:
                break
            file_content["test_metadata"] += [item.model_dump() for item in test_metadata.items]
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
        test_metadata_directory = (
            Path(self._test_result_dir)
            / repository
            / workflow_name
            / job.name
            / self._test_metadata_dir
        )
        test_metadata_directory.mkdir(parents=True, exist_ok=True)
        file_path = test_metadata_directory / f"{job.job_number}_{job.started_at}.json"
        if file_path.exists():
            self.logger.info(f"{file_path} already exists, skipping download.")
        else:
            file_path.write_text(json.dumps(file_content, default=str))
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
        junit_artifacts: list[Artifact] = []
        coverage_artifacts: list[Artifact] = []
        next_page_token: str | None = None
        while True:
            artifacts: ArtifactGroup = self._client.get_job_artifacts(
                organization, repository, str(job.job_number), next_page_token
            )
            if not artifacts:
                break
            for item in artifacts.items:
                filename = Path(item.path).name
                if filename.endswith(".xml"):
                    junit_artifacts.append(item)
                elif re.match(COVERAGE_FILE_REGEX, filename, re.IGNORECASE):
                    coverage_artifacts.append(item)
            next_page_token = artifacts.next_page_token
            if not next_page_token:
                break
        if junit_artifacts:
            self.export_artifacts(
                repository, workflow_name, self._junit_artifact_dir, job, junit_artifacts
            )
        if coverage_artifacts:
            self.export_artifacts(
                repository, workflow_name, self._coverage_artifact_dir, job, coverage_artifacts
            )

    def export_artifacts(
        self,
        repository: str,
        workflow_name: str,
        artifact_directory: str,
        job: Job,
        artifacts: list[Artifact],
    ):
        """Export a given list of test artifacts.

        Args:
            repository (str): The repository name.
            workflow_name (str): The workflow name.
            artifact_directory (str): The destination directory name for artifacts.
            job (Job): The job details.
            artifacts (list[Artifact]): The list of artifacts.

        Raises:
            CircleCIClientError: If there is an error in the CircleCI API request.
            CircleCIScraperError: If there is an error in downloading the artifacts.
        """
        artifact_path = (
            Path(self._test_result_dir)
            / repository
            / workflow_name
            / job.name
            / artifact_directory
            / f"{str(job.job_number)}_{job.started_at}"
        )
        if artifact_path.exists():
            self.logger.info(f"{artifact_path} already exists, skipping download(s).")
            return

        artifact_path.mkdir(parents=True)
        for index, artifact in enumerate(artifacts):
            file_path: Path = artifact_path / f"{index}-{Path(artifact.path).name}"
            self.download_artifact(file_path, artifact.url)

    def download_artifact(self, file_name: Path, url: str) -> None:
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
