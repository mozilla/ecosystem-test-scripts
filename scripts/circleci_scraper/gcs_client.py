# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""GCSClient and related objects"""

import logging

from google.cloud.storage import Client


class GCSClient:
    """Client to interact with GCS."""

    def __init__(self, gcs_client: Client, test_result_bucket: str):
        """Initialize the GCSClient."""
        self._client: Client = gcs_client
        self._bucket = self._client.bucket(test_result_bucket)

    def upload_artifact(self, path: str, content: bytes) -> None:
        """Upload artifact content to GCS."""
        blob = self._bucket.blob(path)
        existing_files = list(self._bucket.list_blobs(prefix=path))
        if existing_files:
            logging.info(f"Skipping {path}, file already exists in GCS")
            return
        blob.upload_from_string(content)
        logging.info(f"Uploaded {path} to GCS bucket")
