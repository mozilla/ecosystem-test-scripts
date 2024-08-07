# `run_circleci_scraper`

Run the CircleCI scraper.

## USAGE

```sh
make run_circleci_scraper
```

In order to use this command, you need to make sure you set your [personal CircleCI token](https://circleci.com/docs/managing-api-tokens/) in your local config.ini file, as seen below:

```ini
[circleci_scraper]
token = <YoUr_tOkEn_hErE>
```

By default, only the 2 previous days of data is fetched. If you want to customize how many previous days are fetched, you can set the `days_of_data` option in your local config.ini file:

```ini
[circleci_scraper]
;(optional) Get data starting from x days past from now (default: all available data)
days_of_data = 7
```

If you have the previous day's data stored locally, the cached data will be used and not re-fetched from CircleCI.

## SEE ALSO

- [`run_test_metric_reporter`](./run_test_metric_reporter.md) -- Run the Test Metric Reporter.
