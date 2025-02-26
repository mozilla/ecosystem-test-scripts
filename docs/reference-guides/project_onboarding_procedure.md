# Project Onboarding Procedure

Below are step-by-step instructions on how to onboard a project to report test metrics.

## Prerequisites

To report test metrics for a project, ensure the following requirements are met:
- Test results must be in JUnit format.
- Coverage results must be in JSON format.
- Supported test frameworks are listed in the 
  [Metric Interpretation Guide][Metric Interpretation Guide].

## 1. Setup CICD to push test result and coverage data to GCS

- Create a directory for the repository in the
  [ecosystem-test-eng-metrics GCP Cloud Bucket][GCP Cloud Bucket].
- Set up a [service account][ETE GCP Service Accounts] for the project with `Storage Object Creator`
  and `Storage Object Viewer` permissions. Store the credentials in the ETE 1Password vault.
- Update project CICD jobs to push Coverage JSON files and JUnit XML files to the GCS repository
  directory, under `coverage` and `junit` subdirectories respectively.
- Coverage JSON files must follow a strict naming convention:
    ```text
  {job_number}__{utc_epoch_datetime}__{repository}__{workflow}__{test_suite}__coverage.xml
  ```
  - Example: `15592__1724283071__autopush-rs__build-test-deploy__integration__coverage.json`
- JUnit XML files must follow a strict naming convention:
  ```text
  {job_number}__{utc_epoch_datetime}__{repository}__{workflow}__{test_suite}__results{-index}.xml
  ```
  - Example: `15592__1724283071__autopush-rs__build-test-deploy__integration__results.xml`
  - The index is optional and can be used in cases of parallel test execution

    

## 2. Create and Populate Tables in the ETE BigQuery Dataset

- **Create Tables**:
  - For test results, create one empty table named `{project_name}_results`.
  - For coverage results, create one empty table named `{project_name}_coverage`.
  - These tables should be created in the `test_metrics` dataset of the 
    [ETE BigQuery instance][ETE BigQuery]. Reference the 
    [official documentation][BigQuery Documentation] to create empty tables with schema definitions.
    Schemas can be copied from existing project tables.
- **Populate Tables**:
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
[ETE BigQuery]: https://console.cloud.google.com/bigquery?cloudshell=false&project=ecosystem-test-eng
[ETE Looker]: https://mozilla.cloud.looker.com/projects/ecosystem-test-eng
[ETE Looker Dashboards]: https://mozilla.cloud.looker.com/boards/140
[ETE GCP Service Accounts]: https://console.cloud.google.com/iam-admin/serviceaccounts?project=ecosystem-test-eng
[GCP Cloud Bucket]: https://console.cloud.google.com/storage/browser/ecosystem-test-eng-metrics
[Github ETE Looker]: https://github.com/mozilla/looker-ecosystem-test-eng
[Metric Interpretation Guide]: ../reference-guides/metric_interpretation_guide.md
[Mozilla Confluence]: https://mozilla-hub.atlassian.net/wiki/spaces/SRE/pages/27920436/Looker
