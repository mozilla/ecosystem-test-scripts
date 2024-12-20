# Developer Setup

Below are step-by-step instructions on how to set up a development environment in order to be able
to successfully contribute to and execute the ecosystem test scripts.

## 1. Clone the ecosystem-test-scripts repository

The ecosystem test scripts are hosted on the [Mozilla Github][Mozilla Github] and can be cloned
using the method of your choice (see [Github Cloning A Repository][Github Cloning A Repository]).
Contributors should follow the [Contributing Guidelines][Contributing Guidelines] and
[Community Participation Guidelines][Community Participation Guidelines] for the repository.

## 2. Create a CircleCI API Token

In order to execute the `circleci_scraper` script, a personal CircleCI API Token is needed. To
create a token, follow the [creating a personal api token][CircleCI Create API Token] CircleCI
instructions. Store the key value in a safe place.

**DO NOT SHARE YOUR CIRCLECI API TOKEN**

## 3. Copy the BigQuery and Google Sheet Service Account JSON Keys

The `metric_reporter` and `google_sheet_uploader` scripts are set up using the 
[ecosystem-test-eng GCP project][ETE GCP Project] with the metric-reporter and metric-gsheet
[service accounts][ETE GCP Service Accounts] respectively. In order to execute these scripts, keys
for these service account, in the form of JSON files, need to be copied from the 1Password Ecosystem
Test Engineering Team Vault into the root directory of the `ecosystem-test-scripts` project.

## 4. Set up the config.ini

All settings for the `ecosystem-test-scripts` are defined in the `config.ini` file. To set up a 
local `config.ini` file:

4.1 Make a copy of the `config.ini.sample` file found in the root directory of the
    `ecosystem-test-scripts` project and rename it to `config.ini`\
4.2 Under the `[circleci_scraper]` section of the file, set the `token` value to the CircleCI API
    key created in step 2

## 5. Copy the latest raw data locally

By default, CircleCI has a retention policy of 30 days for artifacts and 90 days for uploaded test
results; However, we have over a years worth of data gathered for some projects. In order to produce
reports with full trend data and reduce scraping time, copy the latest `raw_data` from the
[ETE team folder][ETE Drive] to the root directory of the `ecosystem-test-scripts` project.

## 6. Set up the python virtual environment

This project uses [Poetry][Poetry] for dependency management in conjunction with a pyproject.toml
file. While you can use virtualenv to set up the dev environment, it is recommended to use
[pyenv][Pyenv] and [pyenv-virtualenv][pyenv-virtualenv], as they work nicely with [Poetry][Poetry].
Once poetry is installed, dependencies can be installed using the following Make command from the
root directory:

```shell
make install
```

For more information on Make commands, run:

```shell
make help
```

## 7. Start Developing!

[CircleCI Create API Token]: https://circleci.com/docs/managing-api-tokens/#creating-a-personal-api-token
[Community Participation Guidelines]: https://github.com/mozilla/ecosystem-test-scripts/blob/main/CODE_OF_CONDUCT.md
[Contributing Guidelines]: https://github.com/mozilla/ecosystem-test-scripts/blob/main/CONTRIBUTING.md
[ETE Drive]: https://drive.google.com/drive/folders/1N4YW97gEH6gmdlfDNtuGxUsdo2EKkCAi
[ETE GCP Project]: https://console.cloud.google.com/welcome?project=ecosystem-test-eng
[ETE GCP Service Accounts]: https://console.cloud.google.com/iam-admin/serviceaccounts?project=ecosystem-test-eng
[Github Cloning A Repository]: https://docs.github.com/en/repositories/creating-and-managing-repositories/cloning-a-repository
[Mozilla Github]: https://github.com/mozilla/ecosystem-test-scripts/
[Poetry]: https://python-poetry.org/docs/#installing-with-pipx
[Pyenv]: https://github.com/pyenv/pyenv#installation
[pyenv-virtualenv]: https://github.com/pyenv/pyenv-virtualenv#installation
