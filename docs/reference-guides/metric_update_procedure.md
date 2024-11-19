# Metric Update Procedure

Please follow the steps below to update the following Google Sheets:

- [Autopush-rs Metrics][1]
- [FxA Metrics][2]
- [Merino-py Metrics][3]

The sheets are typically updated on Monday mornings (North America ET/PT) to ensure the values are
available for team check-in meetings. The process of updating all three Google Sheets can take up
to 10 minutes.

## Prerequisites

Before updating the test metrics, ensure that:

- Your development environment is setup with proper permissions (see [Developer Setup][4]).
- You are on the latest version of the `main` branch
- Your `config.ini` file in the root directory is up to date
- You have the latest raw data in the ecosystem-test-scripts root directory.
  - The raw data should be found in the `test_result_dir` specified in the config.ini file and is
    typically named `raw_data`.
  - The latest raw data is available in the [ETE team folder][0]

## 1. Scrape for New Raw Test Data

To retrieve the latest test and coverage results for local parsing, execute the following command from the ecosystem-test-scripts root directory:

```shell
make run_circleci_scraper
```

_**Notes**:_

- Set the `days_of_data` option in the config.ini file to the appropriate number of days. This is
  typically `8` days since the update cadence is weekly on Mondays.

## 2. Create new CSV reports

To generate CSV reports with the latest test results, test averages, and test coverages, execute the
following command from the ecosystem-test-scripts root directory:

```shell
make run_metric_reporter
```

_**Notes**:_

- The reports will be output to the `reports_dir` specified in the config.ini file. Typically, this
  is a reports directory in the ecosystem-test-scripts root.
- Average reports are produced only after 90 days of data is available. Therefore, some test suites
  may not have these reports.
- Coverage reports are produced only for Autopush-rs unit tests and Merino-py unit and integration
  tests.

## 3. Import CSVs to Google Spreadsheets & Update Trend Table Dates

### 3.1 Import CSVs to Google Spreadsheets

To import the generated CSVs into the 3 different Google Spreadsheets, execute the following make
command:

```shell
make run_google_sheet_uploader
```

This will go through the `reports` folder and import the CSV files into the right Google spreadsheet
and tab. This will happen based on the mapping in the `config.ini` file.

_**Notes**:_

- If the report being imported is a results or coverage report. It may be necessary to convert the
  type of the date column to 'plain text' so that the graphs display at an even cadence.
  - Highlight the `Date` column and in the top menu select `Format > Number > Plain text`

### 3.2 Update Trend Table Dates

- At the beginning of each week, in the Weekly Trends table:
  - Update the `End` date to the current monday date
  - Update the `Start` date to the last monday date
  - Increment the week number
  - **Example:**
    - For week 40 in 2024, the `Start` value is 2024-09-30 and the `End` value is 2024-10-07

- At the end of the quarter, in the Quarterly Trends table
  - Update the `End` date to the last date of the quarter
  - Update the `Start` date to the first date of the quarter
  - Increment the quarter number
  - **Example:**
    - For Q3 in 2024, the `Start` value is 2024-07-01 and the `End` value is 2024-09-30


## 4. Backup the latest `test_result_dir` to the ETE team folder

Compress the contents of the `test_result_dir`, typically called 'raw_data,' and replace the file
located in the [ETE team folder][0].


[0]: https://drive.google.com/drive/folders/1N4YW97gEH6gmdlfDNtuGxUsdo2EKkCAi
[1]: https://docs.google.com/spreadsheets/d/1abjtg2e-PHm8JDP5A629KFVA-eBc8I5VtFPcz_UCDQs/edit?usp=drive_link
[2]: https://docs.google.com/spreadsheets/d/1qKwxsSI2RNo-qKZflETtBbyZ9b0ZUB_id2SL17_MmYo/edit?usp=drive_link
[3]: https://docs.google.com/spreadsheets/d/1dZjfFVoYYPHmStCbyQkWXfBy9yvL10-g6OLQ3nU_25o/edit?usp=drive_link
[4]: ../developer-guides/developer_setup.md