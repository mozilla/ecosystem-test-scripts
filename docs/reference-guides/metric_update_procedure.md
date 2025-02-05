# Metric Update Procedure

Please follow the steps below to update the [ETE Looker Dashboards][ETE Looker Dashboards]. The
dashboards are typically updated on Monday mornings (North America ET/PT) to ensure the values are
available for team check-in meetings. The process of updating the dashboards can take up to 10
minutes.

## Prerequisites

Before updating the test metrics, ensure that:

- Your development environment is setup with proper permissions (see the
  [Developer Setup][Developer Setup Guide]).
- You are on the latest version of the `main` branch
- Your `config.ini` file in the root directory is up-to-date
- You have the latest raw data in the ecosystem-test-scripts root directory.
  - The raw data should be found in the `test_result_dir` specified in the config.ini file and is
    typically named `raw_data`.
  - The latest raw data is available in the
    [ecosystem-test-eng-metrics GCP Cloud Bucket][GCP Cloud Bucket]

## 1. Scrape for New Raw Test Data

To retrieve the latest test and coverage results for local parsing, execute the following command
from the ecosystem-test-scripts root directory:

```shell
make run_circleci_scraper
```

_**Notes**:_

- Set the `days_of_data` option in the config.ini file to the appropriate number of days. This is
  typically `8` days since the update cadence is weekly on Mondays.

## 2. Push updates to BigQuery

To push data to BigQuery and generate CSV reports with the latest test results, test averages, and
test coverages, execute the following command from the ecosystem-test-scripts root directory:

```shell
make run_metric_reporter
```

_**Notes**:_

- Average data is produced only after 90 days of data is available. Therefore, some test suites
  may not have these values.
- Coverage results are produced only for Autopush-rs unit tests and Merino-py unit and integration
  tests.


## 3. Backup the latest `test_result_dir` to the GCP Cloud Bucket

Upload the new contents of the `test_result_dir`, typically called 'raw_data', to the
[ecosystem-test-eng-metrics GCP Cloud Bucket][GCP Cloud Bucket].

[Developer Setup Guide]: ../developer-guides/developer_setup.md
[ETE Looker Dashboards]: https://mozilla.cloud.looker.com/boards/140
[GCP Cloud Bucket]: https://console.cloud.google.com/storage/browser/ecosystem-test-eng-metrics