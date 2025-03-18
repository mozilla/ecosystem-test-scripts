# Project Onboarding Procedure

Below are step-by-step instructions on how to onboard a project to report test metrics.

## Prerequisites

To report test metrics for a repository, contributors must ensure the following requirements are met:
- Test results must be in JUnit XML format.
- Coverage results must be in JSON format.
- Supported test frameworks are listed in the 
  [Metric Interpretation Guide][Metric Interpretation Guide]. If a test framework is not listed,
  contact the [ETE team][ETE Slack] to look into adding support.

## 1. Setup CICD to push test result and coverage data to GCS

- **GCP Admin Requirement**: To create a cloud bucket and a service user with access to the bucket
  in the [ecosystem-test-eng GCP][ETE GCP] project, administrative permissions are required. Contact
  the [ETE team][ETE Slack].
- **Create A Cloud Bucket (ETE Team)**: Create a directory for the repository in the
  [ecosystem-test-eng-metrics GCS][ETE GCS].
- **Set up a Service User (ETE Team)**:
  - If test artifacts are being pushed by **GitHub Actions**:
    - Set up a [service account][ETE GCP Service Accounts] for the project with 
      `Storage Object Creator` and `Storage Object Viewer` permissions
    - The service account name should be `{repository}-github`
    - Allow the GitHub repo to use this service account:
      - On the Service accounts page, click your service account 
      - Go to the PERMISSIONS tab
      - Under VIEW BY PRINCIPALS, click GRANT ACCESS 
      - Add this principal: `principalSet://iam.googleapis.com/projects/324168772199/locations/global/workloadIdentityPools/github-actions/attribute.repository/OWNER/REPOSITORY`
      - Assign this role: Workload Identity User
    - Configs are expected to use the
      [Google Cloud Authentication GitHub Action][Google Cloud Authentication GitHub Action]
      with the `service_account` set to the above and the `workload_identity_provider` set to 
      `${{ vars.GCPV2_GITHUB_WORKLOAD_IDENTITY_PROVIDER }}`
  - If test artifacts are being pushed by [CircleCI][CircleCI]:
    - Set up a [service account][ETE GCP Service Accounts] for the project with 
      `Storage Object Creator` and `Storage Object Viewer` permissions
    - The service account name should be `{repository}-circleci`
    - Create a JSON key
    - Store the credentials in the ETE 1Password vault
    - Configs are expected to use the [CircleCI gcp-cli orb][CircleCI gcp-cli orb]
    - In CircleCI under 'Project Settings > Environment Variables':
      - Option 1: Set the default environment variables for the orb `GCLOUD_SERVICE_KEY` with the 
        JSON key contents and `GOOGLE_PROJECT_ID` to `ecosystem-test-eng`
      - Option 2: If the default environment variables are already in use, override the 
        `gcp-cli/setup` setup variables with the following environment variables. 
        `ETE_GCLOUD_SERVICE_KEY` which should be set with the JSON key contents and 
        `ETE_GOOGLE_PROJECT_ID` which should be set to `ecosystem-test-eng`
- **Modify CICD**:
  - Update project CICD jobs to push Coverage JSON files and JUnit XML files to the GCS repository
    directory, under `coverage` and `junit` subdirectories respectively.
  - Coverage JSON files must follow a strict naming convention:
      ```text
    {job_number}__{utc_epoch_datetime}__{repository}__{workflow}__{test_suite}__coverage.json
    ```
    - Example: `15592__1724283071__autopush-rs__build-test-deploy__integration__coverage.json`
  - JUnit XML files must follow a strict naming convention:
    ```text
    {job_number}__{utc_epoch_datetime}__{repository}__{workflow}__{test_suite}__results{-index}.xml
    ```
    - Example: `15592__1724283071__autopush-rs__build-test-deploy__integration__results.xml`
    - The index is optional and can be used in cases of parallel test execution

## 2. Create and Populate Tables in the ETE BigQuery Dataset

- **GCP Admin Requirement**: To create and populate tables in the [ecosystem-test-eng GCP][ETE GCP]
  project, administrative permissions are required. Contact the [ETE team][ETE Slack].
- **Create Tables (ETE Team)**:
  - For test results, create one empty table named `{project_name}_results`.
  - For coverage results, create one empty table named `{project_name}_coverage`.
  - These tables should be created in the `test_metrics` dataset of the 
    [ETE BigQuery instance][ETE BigQuery]. Reference the 
    [official documentation][BigQuery Documentation] to create empty tables with schema definitions.
    Schemas can be copied from existing project tables.
- **Populate Tables (ETE Team)**:
  - Execute the following command to populate the tables with data:
    ```shell
    make run_metric_reporter
    ```

## 3. Create a Looker Dashboard

- **License Requirement**:
  A developer license is required to create and edit dashboards in Looker. Instructions for
  obtaining a license and resources for learning Looker are available on the 
  [Mozilla Confluence][Mozilla Confluence]. Additional help can be found in the `#data-help` and
  `#looker-platform-discussion` Slack channels.

- **Update Looker Project**:
  - Update the [ecosystem-test-eng Looker project][ETE Looker] Looker project model and add the
    required views for the new project test data. Related repository: 
    [looker-ecosystem-test-eng][Github ETE Looker].

- **Create Dashboard**:
  Create a new dashboard, populate it with looks for the new project data, and add it to the
  [ETE Test Metrics Board][ETE Looker Dashboards].

[BigQuery Documentation]: https://cloud.google.com/bigquery/docs/tables#create-table
[CircleCI]: https://app.circleci.com/home
[CircleCI gcp-cli orb]: https://circleci.com/developer/orbs/orb/circleci/gcp-cli
[ETE BigQuery]: https://console.cloud.google.com/bigquery?cloudshell=false&project=ecosystem-test-eng
[ETE Looker]: https://mozilla.cloud.looker.com/projects/ecosystem-test-eng
[ETE Looker Dashboards]: https://mozilla.cloud.looker.com/boards/140
[ETE GCP]: https://console.cloud.google.com/storage/overview;tab=overview?project=ecosystem-test-eng
[ETE GCP Service Accounts]: https://console.cloud.google.com/iam-admin/serviceaccounts?project=ecosystem-test-eng
[ETE GCS]: https://console.cloud.google.com/storage/browser/ecosystem-test-eng-metrics
[ETE Slack]: https://mozilla.enterprise.slack.com/archives/CDXKPH2A2
[Github ETE Looker]: https://github.com/mozilla/looker-ecosystem-test-eng
[Google Cloud Authentication GitHub Action]: https://github.com/google-github-actions/auth
[Metric Interpretation Guide]: ../reference-guides/metric_interpretation_guide.md
[Mozilla Confluence]: https://mozilla-hub.atlassian.net/wiki/spaces/SRE/pages/27920436/Looker
