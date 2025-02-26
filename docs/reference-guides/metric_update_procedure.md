# Metric Update Procedure

Please follow the steps below to update the [ETE Looker Dashboards][ETE Looker Dashboards]. The
dashboards are typically updated on Monday mornings (North America ET/PT) to ensure the values are
available for team check-in meetings. The process of updating the dashboards can take up to an hour,
this is due to network latency from parsing files stored on GCS.

## Prerequisites

Before updating the test metrics, ensure that:

- Your development environment is setup with proper permissions (see the
  [Developer Setup][Developer Setup Guide]).
- You are on the latest version of the `main` branch
- Your `config.ini` file in the root directory is up-to-date

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

To push data to BigQuery with the latest test results and test coverages, execute the following
command from the ecosystem-test-scripts root directory:

```shell
make run_metric_reporter
```

_**Notes**:_

- Coverage results are produced only for Autopush-rs unit tests and Merino-py unit and integration
  tests.

[Developer Setup Guide]: ../developer-guides/developer_setup.md
[ETE Looker Dashboards]: https://mozilla.cloud.looker.com/boards/140
