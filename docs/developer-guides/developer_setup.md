# Developer Setup

Below are step-by-step instructions on how to set up a development environment in order to be able
to successfully contribute to and execute the ecosystem test scripts.

# 1. Clone the ecosystem-test-scripts repository

The ecosystem test scripts are hosted on the [Mozilla Github][0] and can be cloned using the method
of your choice (see [Cloning a repository][1]). Contributors should follow the
[Contributing Guidelines][2] and [Community Participation Guidelines][3] for the repository.

# 2. Create a CircleCI API Token

In order to execute the `circleci_scraper` script, a personal CircleCI API Token is needed. To
create a token, follow the [creating a personal api token][4] CircleCI instructions. Store the key
value in a safe place.

**DO NOT SHARE YOUR CIRCLECI API TOKEN**

# 3. Copy the Google Sheet Service Account JSON Key

The `google_sheet_uploader` script is set up using the [ecosystem-test-eng GCP project][5] with the
[metric-gsheet service account][6]. In order to execute the `google_sheet_uploader` script, a
key for this service account, in the form of a JSON file, needs to be copied from the 1Password
Ecosystem Test Engineering Team Vault into the root directory of the `ecosystem-test-scripts`
project.

# 4. Set up the config.ini

All settings for the `ecosystem-test-scripts` are defined in the `config.ini` file. To set up a 
local `config.ini` file:

4.1 Make a copy of the `config.ini.sample` file found in the root directory of the
    `ecosystem-test-scripts` project and rename it to `config.ini`\
4.2 Under the `[circleci_scraper]` section of the file, set the `token` value to the CircleCI API
    key created in step 2

# 5. Copy the latest raw data locally

By default, CircleCI has a retention policy of 30 days for artifacts and 90 days for uploaded test
results; However, we have over a years worth of data gathered for some projects. In order to produce
reports with full trend data and reduce scraping time, copy the latest `raw_data` from the
[ETE team folder][7] to the root directory of the `ecosystem-test-scripts` project.

# 6. Set up the python virtual environment

This project uses [Poetry][10] for dependency management in conjunction with a pyproject.toml file.
While you can use virtualenv to set up the dev environment, it is recommended to use [pyenv][8] and 
[pyenv-virtualenv][9], as they work nicely with [Poetry][10]. Once poetry is installed, dependencies
can be installed using the following Make command from the root directory:

```shell
make install
```

For more information on Make commands, run:

```shell
make help
```

# 7. Start Developing!

[0]: https://github.com/mozilla/ecosystem-test-scripts/
[1]: https://docs.github.com/en/repositories/creating-and-managing-repositories/cloning-a-repository
[2]: https://github.com/mozilla/ecosystem-test-scripts/blob/main/CONTRIBUTING.md
[3]: https://github.com/mozilla/ecosystem-test-scripts/blob/main/CODE_OF_CONDUCT.md
[4]: https://circleci.com/docs/managing-api-tokens/#creating-a-personal-api-token
[5]: https://console.cloud.google.com/welcome?project=ecosystem-test-eng
[6]: https://console.cloud.google.com/iam-admin/serviceaccounts?project=ecosystem-test-eng
[7]: https://drive.google.com/drive/folders/1N4YW97gEH6gmdlfDNtuGxUsdo2EKkCAi
[8]: https://github.com/pyenv/pyenv#installation
[9]: https://github.com/pyenv/pyenv-virtualenv#installation
[10]: https://python-poetry.org/docs/#installing-with-pipx
