# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""GCSClient and related objects"""

from google.cloud.storage import Client
from pydantic import BaseModel

from scripts.metric_reporter.error import BaseError


class GCSClientError(BaseError):
    """Custom error raised for errors encountered by the GCSClient."""

    pass


class GCSArtifacts(BaseModel):
    """Represents grouped GCS file names for coverage and JUnit artifacts."""

    coverage_artifact_files: list[str] = []
    junit_artifact_files: list[str] = []


class GCSClient:
    """Client to interact with GCS."""

    def __init__(
        self,
        gcs_client: Client,
        test_result_bucket: str,
        coverage_artifact_dir: str,
        junit_artifact_dir: str,
    ) -> None:
        """Initialize the GCSClient.

        Args:
            gcs_client (Client): Client to interact with GCS.
            test_result_bucket (str): Name of the test result bucket.
            coverage_artifact_dir (str): Name of the coverage artifact subdirectory.
            junit_artifact_dir (str): Name of the JUnit artifact subdirectory.
        """
        self._client: Client = gcs_client
        self._bucket = self._client.bucket(test_result_bucket)
        self.coverage_artifact_dir: str = coverage_artifact_dir
        self.junit_artifact_dir: str = junit_artifact_dir

    def get_artifacts(self) -> list[GCSArtifacts]:
        """Get artifact files from GCS, grouped by repository.

        Returns:
            List[GCSArtifactPaths]: A list of grouped GCS paths per repository.

        Raises:
            GCSClientError: If the structure of the test_result_bucket is unexpected
        """
        # Here we assume that the structure of the test_result_bucket is as follows:
        # test_result_bucket/
        #     ├── repository/
        #          ├── coverage_artifact_dir/
        #               ├── coverage-1.json
        #               ├── coverage-2.json
        #          ├── junit_artifact_dir/
        #               ├── junit-1.xml
        #               ├── junit-2.xml
        artifact_map = {}  # Using a regular dictionary
        for blob in self._client.list_blobs(self._bucket):
            parts = blob.name.rstrip("/").split("/")
            if len(parts) != 3:
                continue
            repository, artifact_dir, artifact_file = parts

            if repository not in artifact_map:
                artifact_map[repository] = GCSArtifacts()

            if artifact_dir == self.coverage_artifact_dir:
                artifact_map[repository].coverage_artifact_files.append(artifact_file)
            elif artifact_dir == self.junit_artifact_dir:
                artifact_map[repository].junit_artifact_files.append(artifact_file)
            else:
                raise GCSClientError(
                    f"The artifact directory name {artifact_dir} from {blob.name} is unsupported."
                )

        return list(artifact_map.values())

    def get_coverage_artifact_content(self, repository: str, file_name: str) -> str:
        """Get the content of a coverage artifact.

        Args:
            repository (str): The repository name.
            file_name (str): The file name.

        Returns:
            str: Coverage JSON file content.
        """
        return self._get_artifact_content(repository, self.coverage_artifact_dir, file_name)

    def get_junit_artifact_content(self, repository: str, file_name: str) -> str:
        """Get the content of a JUnit artifact.

        Args:
            repository (str): The repository name.
            file_name (str): The file name.

        Returns:
            str: JUnit XML file content.
        """
        return self._get_artifact_content(repository, self.junit_artifact_dir, file_name)

    def _get_artifact_content(self, repository: str, artifact_dir: str, file_name: str) -> str:
        blob_name = f"{repository}/{artifact_dir}/{file_name}"
        blob = self._bucket.blob(blob_name)
        content: str = blob.download_as_text()
        return content
