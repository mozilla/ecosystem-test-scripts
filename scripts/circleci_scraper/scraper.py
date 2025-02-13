# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""CircleCIScraper and related objects"""

import logging
import re
from pathlib import Path
from datetime import datetime, timezone

import requests
from requests.exceptions import RequestException

from client import (
    CircleCIClient,
    PipelineGroup,
    WorkflowGroup,
    JobGroup,
    Job,
    ArtifactGroup,
    Artifact,
    Workflow,
)
from scripts.circleci_scraper.config import (
    CircleCIScraperJobConfig,
    CircleCIScraperPipelineConfig,
)
from scripts.circleci_scraper.gcs_client import GCSClient
from scripts.common.config import CommonConfig
from scripts.common.constants import DATETIME_FORMAT, DATETIME_MILLISECOND_FORMAT
from scripts.common.error import BaseError

COVERAGE_FILE_REGEX = r".*cov.*\.json$"
CANCELED_JOB_STATUS = "canceled"
RUNNING_JOB_STATUS = "running"


class CircleCIScraperError(BaseError):
    """Custom exception class for CircleCIScraper errors."""

    pass


class CircleCIScraper:
    """Export CircleCI test artifacts."""

    logger = logging.getLogger(__name__)

    def __init__(
        self, common_config: CommonConfig, client: CircleCIClient, gcs_client: GCSClient
    ) -> None:
        """Initialize the CircleCIScraper.

        Args:
            common_config (CommonConfig): Directory information to store test results.
            client (CircleCIClient): The CircleCI client to interact with the API.
            gcs_client (GCSClient): The GCS client to interact with storage.
        """
        self._client = client
        self._junit_artifact_dir = common_config.junit_artifact_dir
        self._coverage_artifact_dir = common_config.coverage_artifact_dir
        self._gcs_client: GCSClient = gcs_client

    def export_test_artifacts(
        self,
        pipeline_configs: list[CircleCIScraperPipelineConfig],
        date_limit: datetime | None = None,
    ) -> None:
        """Export test artifacts for a list of pipelines.

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
            self.export_artifacts_by_pipeline(pipeline_config, date_limit)

    def export_artifacts_by_pipeline(
        self, pipeline_config: CircleCIScraperPipelineConfig, date_limit: datetime | None = None
    ) -> None:
        """Export test artifacts for a single pipeline.

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
                    pipeline.created_at, DATETIME_MILLISECOND_FORMAT
                ).replace(tzinfo=timezone.utc)
                if date_limit and created_at_datetime < date_limit:
                    return
                self.export_test_artifacts_by_pipeline_id(
                    pipeline.id,
                    pipeline_config.organization,
                    pipeline_config.repository,
                    pipeline_config.workflows,
                )
            next_page_token = pipelines.next_page_token
            if not next_page_token:
                break

    def export_test_artifacts_by_pipeline_id(
        self,
        pipeline_id: str,
        organization: str,
        repository: str,
        workflow_configs: dict[str, list[CircleCIScraperJobConfig]],
    ) -> None:
        """Export test artifacts for a specific pipeline ID.

        Args:
            pipeline_id (str): The pipeline ID.
            organization (str): The organization name.
            repository (str): The repository name.
            workflow_configs (dict[str, list[CircleCIScraperJobConfig]]): The workflow
                                                                          configurations.

        Raises:
            CircleCIClientError: If there is an error in the CircleCI API request.
            CircleCIScraperError: If there is an error in downloading the artifacts.
        """
        next_page_token: str | None = None
        while True:
            workflows: WorkflowGroup = self._client.get_workflows(pipeline_id, next_page_token)
            for workflow in workflows.items:
                if workflow.name in workflow_configs:
                    job_configs: list[CircleCIScraperJobConfig] = workflow_configs[workflow.name]
                    self.export_test_artifacts_workflow_id(
                        organization, repository, workflow, job_configs
                    )
            next_page_token = workflows.next_page_token
            if not next_page_token:
                break

    def export_test_artifacts_workflow_id(
        self,
        organization: str,
        repository: str,
        workflow: Workflow,
        job_configs: list[CircleCIScraperJobConfig],
    ) -> None:
        """Export test artifacts for a specific workflow ID.

        Args:
            organization (str): The organization name.
            repository (str): The repository name.
            workflow (Workflow): The workflow.
            job_configs (list[CircleCIScraperJobConfig]): A list of job configs.

        Raises:
            CircleCIClientError: If there is an error in the CircleCI API request.
            CircleCIScraperError: If there is an error in downloading the artifacts.
        """
        next_page_token: str | None = None
        while True:
            jobs: JobGroup = self._client.get_jobs(workflow.id, next_page_token)
            for job in jobs.items:
                if job_config := next(
                    (config for config in job_configs if job.name == config.job_name), None
                ):
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
                    self.export_test_artifacts_by_job(
                        organization, repository, workflow.name, job_config.test_suite, job
                    )
            next_page_token = jobs.next_page_token
            if not next_page_token:
                break

    def export_test_artifacts_by_job(
        self,
        organization: str,
        repository: str,
        workflow_name: str,
        test_suite: str,
        job: Job,
    ) -> None:
        """Export test artifacts for a specific job.

        Args:
            organization (str): The organization name.
            repository (str): The repository name.
            workflow_name (str): The workflow name.
            test_suite (str): The test suite name.
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
                repository,
                workflow_name,
                self._junit_artifact_dir,
                test_suite,
                job,
                junit_artifacts,
            )
        if coverage_artifacts:
            self.export_artifacts(
                repository,
                workflow_name,
                self._coverage_artifact_dir,
                test_suite,
                job,
                coverage_artifacts,
            )

    def export_artifacts(
        self,
        repository: str,
        workflow_name: str,
        artifact_directory: str,
        test_suite: str,
        job: Job,
        artifacts: list[Artifact],
    ):
        """Export a given list of test artifacts.

        Args:
            repository (str): The repository name.
            workflow_name (str): The workflow name.
            artifact_directory (str): The destination directory name for artifacts.
            test_suite (str): The test suite name.
            job (Job): The job details.
            artifacts (list[Artifact]): The list of artifacts.

        Raises:
            CircleCIClientError: If there is an error in the CircleCI API request.
            CircleCIScraperError: If there is an error in downloading the artifacts.
        """
        for index, artifact in enumerate(artifacts):
            job_datetime = datetime.strptime(job.started_at, DATETIME_FORMAT).replace(
                tzinfo=timezone.utc
            )
            epoch = int(job_datetime.timestamp())
            artifact_path = Path(artifact.path)
            # FxA doesn't guarantee unique names for their test files, so concatenating the parent
            # directory is a necessary evil atm
            destination_path = (
                f"{repository}/"
                f"{artifact_directory}/"
                f"{str(job.job_number)}__"
                f"{epoch}__"
                f"{repository}__"
                f"{workflow_name}__"
                f"{test_suite}__"
                f"{f'{artifact_path.parent.name.replace("_", "-")}-' if artifact_path.parent.name else ''}"
                f"{artifact_path.name.replace("_", "-")}"
            )
            self.download_artifact(destination_path, artifact.url)

    def download_artifact(self, destination_path: str, url: str) -> None:
        """Download an artifact from the specified URL.

        Args:
            destination_path (str): The destination blob path.
            url (str): The URL of the artifact to download.

        Raises:
            CircleCIScraperError: If there is an error in downloading the artifact.
        """
        try:
            response: requests.Response = requests.get(url, timeout=10)
            response.raise_for_status()
            self._gcs_client.upload_artifact(destination_path, response.content)
        except RequestException as error:
            self.logger.error(f"Failed to download artifact from {url}", exc_info=error)
            raise CircleCIScraperError(f"Failed to download artifact from {url}", error)
