# Project Onboarding Procedure

Below are step-by-step instructions on how to onboard a project to report test metrics.

## Prerequisites

To report test metrics for a project, ensure the following requirements are met:

- The project uses [CircleCI][0] for test execution, and members of the ETE team have access to the
  CircleCI pipelines.
- Testing and coverage results are stored as artifacts in CircleCI jobs:
  - Test results must be in JUnit format.
  - Coverage results must be in JSON format.
  - Supported test frameworks are listed in the [Metric Interpretation Guide][1].

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
- Once scraping is complete, compress the contents of `test_result_dir`, and replace the
  corresponding file in the [ETE team folder][3].

## 2. Create and Populate Tables in the ETE BigQuery Dataset

- **Create Tables**:
  - For test results, create two empty tables using the following naming conventions:
    - `{project_name}_averages`
    - `{project_name}_results`
  - For coverage results, create one empty table named `{project_name}_coverage`.
  - These tables should be created in the `test_metrics` dataset of the [ETE BigQuery instance][4].
    Reference the [official documentation][5] to create empty tables with schema definitions.
    Schemas can be copied from existing project tables.
- **Populate Tables**:
  - Execute the following command to populate the tables with data:
    ```shell
    make run_metric_reporter
    ```

## 3. Create a Looker Dashboard

- **License Requirement**:
  A developer license is required to create and edit dashboards in Looker. Instructions for
  obtaining a license and resources for learning Looker are available on the [Mozilla wiki][6].
  Additional help can be found in the `#data-help` and `#looker-platform-discussion` Slack channels.

- **Update Looker Project**:
  - Update the [ecosystem-test-eng Looker project][7] Looker project model and add the required
    views for the new project test data. Related repository: [looker-ecosystem-test-eng][8].

- **Create Dashboard**:
  Create a new dashboard, populate it with looks for the new project data, and add it to the
  [ETE Test Metrics Board][9].

[0]: https://app.circleci.com/home
[1]: ../reference-guides/metric_interpretation_guide.md
[3]: https://drive.google.com/drive/folders/1N4YW97gEH6gmdlfDNtuGxUsdo2EKkCAi
[4]: https://console.cloud.google.com/bigquery?cloudshell=false&project=ecosystem-test-eng
[5]: https://cloud.google.com/bigquery/docs/tables#create-table
[6]: https://mozilla-hub.atlassian.net/wiki/spaces/SRE/pages/27920436/Looker
[7]: https://mozilla.cloud.looker.com/projects/ecosystem-test-eng
[8]: https://github.com/mozilla/looker-ecosystem-test-eng
[9]: https://mozilla.cloud.looker.com/boards/140
