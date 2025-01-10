# Command Line Tool

## COMMANDS

- [`check`](#check) -- Run linting, formatting, security, and type checks.
- [`clean`](#clean) -- Clean up installation and cache files.
- [`format`](#format) -- Apply formatting.
- [`install`](#install) -- Install dependencies.
- [`run_circleci_scraper`](#run_circleci_scraper) -- Run the CircleCI scraper.
- [`run_google_sheet_uploader`](#run_google_sheet_uploader) -- Run the Test Metric Reporter.
- [`run_metric_reporter`](#run_metric_reporter) -- Run the Test Metric Reporter.
- [`test`](#test) -- Run tests.
- [`test_coverage`](#test_coverage) -- Run tests with coverage reporting.
- [`test_coverage_html`](#test_coverage_html) -- Run tests and generate HTML coverage report.

---

### `install`

Install dependencies.

#### USAGE

```sh
make install
```

#### SEE ALSO

- [`clean`](#clean) -- Clean up installation and cache files.

---

### `clean`

Clean up installation and cache files.

#### USAGE

```sh
make clean
```

#### SEE ALSO

- [`install`](#install) -- Install dependencies.

---

### `check`

Run linting, formatting, security, and type checks.

This script uses the following tools:

- `ruff` -- check for linting issues and code formatting.
- `bandit` -- check for security issues.
- `mypy` -- check for type issues.

#### USAGE

```sh
make check
```

#### SEE ALSO

- [`format`](#format) -- Apply formatting.

---

### `format`

Apply formatting.

This script will use `ruff` to automatically fix linting issues and format the code.

#### USAGE

```sh
make format
```

#### SEE ALSO

- [`check`](#check) -- Run linting, formatting, security, and type checks.

---

### `test`

Run tests.

#### USAGE

```sh
make test
```

#### SEE ALSO

- [`test_coverage`](#test_coverage) -- Run tests with coverage reporting.
- [`test_coverage_html`](#test_coverage_html) -- Run tests and generate HTML coverage report.

---

### `test_coverage`

Run tests with coverage reporting.

#### USAGE

```sh
make test_coverage
```

#### SEE ALSO

- [`test`](#test) -- Run tests.
- [`test_coverage_html`](#test_coverage_html) -- Run tests and generate HTML coverage report.

### `test_coverage_html`

Run tests and generate HTML coverage report.

#### USAGE

```sh
make test_coverage_html
```

#### SEE ALSO

- [`test`](#test) -- Run tests.
- [`test_coverage`](#test_coverage) -- Run tests with coverage reporting.

---

### `run_circleci_scraper`

Run the CircleCI scraper.

#### USAGE

```sh
make run_circleci_scraper
```

In order to use this command, you need to make sure you set your [personal CircleCI token](https://circleci.com/docs/managing-api-tokens/) in your local config.ini file, as seen below:

```ini
[circleci_scraper]
token = <YoUr_tOkEn_hErE>
```

If the `days_of_data` option is not present in the config.ini file, the default of "all available data" will be fetched. If you want to customize how many previous days are fetched, you can set the `days_of_data` option in your local config.ini file:

```ini
[circleci_scraper]
;(optional) Get data starting from x days past from now (default: all available data)
days_of_data = 7
```

If you have the previous day's data stored locally, the cached data will be used and not re-fetched from CircleCI.

#### SEE ALSO

- [`run_metric_reporter`](#run_metric_reporter) -- Run the Test Metric Reporter.

---

### `run_google_sheet_uploader`

Run the Google Sheet Uploader.

#### USAGE

```sh
make run_google_sheet_uploader
```

---

### `run_metric_reporter`

Run the Test Metric Reporter.

#### USAGE

```sh
make run_metric_reporter
```

#### SEE ALSO

- [`run_circleci_scraper`](#run_circleci_scraper) -- Run the CircleCI scraper.
