# Developer Setup

Below are step-by-step instructions on how to set up a development environment in order to be able
to successfully contribute to and execute the ecosystem test scripts.

## 1. Clone the ecosystem-test-scripts repository

The ecosystem test scripts are hosted on the [Mozilla Github][Mozilla Github] and can be cloned
using the method of your choice (see [Github Cloning A Repository][Github Cloning A Repository]).
Contributors should follow the [Contributing Guidelines][Contributing Guidelines] and
[Community Participation Guidelines][Community Participation Guidelines] for the repository.

## 2. Copy the Metric Reporter Service Account JSON Key

The `metric_reporter` script is set up using the [ecosystem-test-eng GCP project][ETE GCP Project]
with the metric-reporter [service accounts][ETE GCP Service Accounts]. In order to execute the
script, a key for the service account, in the form of a JSON file, needs to be copied from the
1Password Ecosystem Test Engineering Team Vault into the root directory of the 
`ecosystem-test-scripts` project.

## 3. Set up the config.ini

All settings for the `ecosystem-test-scripts` are defined in the `config.ini` file. To set up a 
local `config.ini` file, make a copy of the `config.ini.sample` file found in the root directory of
the ecosystem-test-scripts` project and rename it to `config.ini`

## 4. Set up the python virtual environment

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

## 5. Start Developing!

[Community Participation Guidelines]: https://github.com/mozilla/ecosystem-test-scripts/blob/main/CODE_OF_CONDUCT.md
[Contributing Guidelines]: https://github.com/mozilla/ecosystem-test-scripts/blob/main/CONTRIBUTING.md
[ETE GCP Project]: https://console.cloud.google.com/welcome?project=ecosystem-test-eng
[ETE GCP Service Accounts]: https://console.cloud.google.com/iam-admin/serviceaccounts?project=ecosystem-test-eng
[Github Cloning A Repository]: https://docs.github.com/en/repositories/creating-and-managing-repositories/cloning-a-repository
[Mozilla Github]: https://github.com/mozilla/ecosystem-test-scripts/
[Poetry]: https://python-poetry.org/docs/#installing-with-pipx
[Pyenv]: https://github.com/pyenv/pyenv#installation
[pyenv-virtualenv]: https://github.com/pyenv/pyenv-virtualenv#installation
