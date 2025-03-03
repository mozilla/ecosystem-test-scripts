# Command Line Tool

## COMMANDS

- [`check`](#check) -- Run linting, formatting, security, and type checks.
- [`clean`](#clean) -- Clean up installation and cache files.
- [`format`](#format) -- Apply formatting.
- [`install`](#install) -- Install dependencies.
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

### `run_metric_reporter`

Run the Test Metric Reporter.

#### USAGE

```sh
make run_metric_reporter
```
