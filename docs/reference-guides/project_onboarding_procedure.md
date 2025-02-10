# Project Onboarding Procedure

Below are step-by-step instructions on how to onboard a project to report test metrics.

## Prerequisites

To report test metrics for a project, ensure the following requirements are met:

- The project uses [CircleCI][CircleCI] for test execution, and members of the ETE team have access
  to the CircleCI pipelines.
- Testing and coverage results are stored as artifacts in CircleCI jobs:
  - Test results must be in JUnit format.
  - Coverage results must be in JSON format.
  - Supported test frameworks are listed in the 
    [Metric Interpretation Guide][Metric Interpretation Guide].

## 1. Add CircleCI Pipelines to the Config File and Scrape Historical Data

- Add the new CircleCI pipelines under the `circleci_scraper` section in your local `config.ini` and
  `config.ini.sample`. Push changes to the `config.ini.sample` to the repository to keep
  contributors up-to-date.
- Execute the `circleci_scraper` using the following command. Ensure the `days_of_data` option in
  the `circleci_scraper` section of `config.ini` is omitted to scrape all available historical data.
  Test and coverage data will be stored locally in the `test_result_dir` (typically called
  `raw_data` at the project root).
  ```shell
  make run_circleci_scraper
  ```
- Once scraping is complete, upload the new contents of the `test_result_dir` to the
  [ecosystem-test-eng-metrics GCP Cloud Bucket][GCP Cloud Bucket].

## 2. Create and Populate Tables in the ETE BigQuery Dataset

- **Create Tables**:
  - For test results, create two empty tables using the following naming conventions:
    - `{project_name}_averages`
    - `{project_name}_results`
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
[GCP Cloud Bucket]: https://console.cloud.google.com/storage/browser/ecosystem-test-eng-metrics
[Github ETE Looker]: https://github.com/mozilla/looker-ecosystem-test-eng
[Metric Interpretation Guide]: ../reference-guides/metric_interpretation_guide.md
[Mozilla Confluence]: https://mozilla-hub.atlassian.net/wiki/spaces/SRE/pages/27920436/Looker
