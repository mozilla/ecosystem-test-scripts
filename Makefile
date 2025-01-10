SCRIPTS_DIR := scripts
TESTS_DIR := tests
CHECK_DIRS := $(SCRIPTS_DIR) $(TESTS_DIR)
POETRY := poetry
PYPROJECT_TOML := pyproject.toml
POETRY_LOCK := poetry.lock
INSTALL_STAMP := .install.stamp

# Check if Poetry is installed by looking for its command in the system path
POETRY_CHECK := $(shell command -v $(POETRY) 2> /dev/null)

.PHONY: help
help:
	@echo "Available targets:"
	@echo "  install                   Install dependencies"
	@echo "  check                     Run linting, formatting, security, and type checks"
	@echo "  format                    Apply formatting"
	@echo "  test                      Run tests"
	@echo "  test_coverage             Run tests with coverage reporting"
	@echo "  test_coverage_html        Run tests and generate HTML coverage report"
	@echo "  clean                     Clean up installation and cache files"
	@echo "  run_circleci_scraper      Run the CircleCI scraper"
	@echo "  run_google_sheet_uploader Run the Google Sheet Uploader"
	@echo "  run_metric_reporter       Run the Metric Reporter"

.PHONY: install
install: $(INSTALL_STAMP)

$(INSTALL_STAMP): $(PYPROJECT_TOML) $(POETRY_LOCK)
	@if [ -z "$(POETRY_CHECK)" ]; then \
		echo "Poetry could not be found. See https://python-poetry.org/docs/"; \
		exit 2; \
	fi
	$(POETRY) install --no-root --with circleci_scraper,metric_reporter,google_sheet_uploader,dev
	# Create an empty install stamp file to indicate that dependencies have been installed
	touch $(INSTALL_STAMP)

.PHONY: check
check: $(INSTALL_STAMP)
	# Run ruff to check for linting issues in the scripts and tests directories
	$(POETRY) run ruff check $(CHECK_DIRS)
	# Run ruff to check the formatting in the scripts and tests directories
	$(POETRY) run ruff format --check $(CHECK_DIRS)
	# Run bandit to check for security issues
	$(POETRY) run bandit --quiet -r -c $(PYPROJECT_TOML) $(CHECK_DIRS)
	# Run mypy to check for type issues
	$(POETRY) run mypy --config-file=$(PYPROJECT_TOML) $(CHECK_DIRS)

.PHONY: format
format: $(INSTALL_STAMP)
	# Run ruff to automatically fix linting issues in the scripts and tests directories
	$(POETRY) run ruff check --fix $(CHECK_DIRS)
	# Run ruff to format the scripts and tests directories
	$(POETRY) run ruff format $(CHECK_DIRS)

.PHONY: test
test: $(INSTALL_STAMP)
	$(POETRY) run pytest $(TESTS_DIR)

.PHONY: test_coverage
test_coverage: $(INSTALL_STAMP)
	$(POETRY) run pytest $(TESTS_DIR) --cov=$(SCRIPTS_DIR) --cov-report=term-missing

.PHONY: test_coverage_html
test_coverage_html: $(INSTALL_STAMP)
	$(POETRY) run pytest $(TESTS_DIR) --cov=$(SCRIPTS_DIR) --cov-report=html

.PHONY: clean
clean:
	rm -f $(INSTALL_STAMP)
	rm -f .coverage
	rm -rf .mypy_cache
	rm -rf .ruff_cache
	rm -rf .pytest_cache
	rm -rf htmlcov

.PHONY: run_circleci_scraper
run_circleci_scraper: $(INSTALL_STAMP)
	PYTHONPATH=. $(POETRY) run python $(SCRIPTS_DIR)/circleci_scraper/main.py --config=config.ini

.PHONY: run_google_sheet_uploader
run_google_sheet_uploader: $(INSTALL_STAMP)
	PYTHONPATH=. $(POETRY) run python $(SCRIPTS_DIR)/google_sheet_uploader/main.py --config=config.ini

.PHONY: run_metric_reporter
run_metric_reporter: $(INSTALL_STAMP)
	PYTHONPATH=. $(POETRY) run python $(SCRIPTS_DIR)/metric_reporter/main.py --config=config.ini
