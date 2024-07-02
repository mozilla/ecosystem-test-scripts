SCRIPT_DIR := scripts
POETRY := poetry
PYPROJECT_TOML := pyproject.toml
POETRY_LOCK := poetry.lock
INSTALL_STAMP := .install.stamp

# Check if Poetry is installed by looking for its command in the system path
POETRY_CHECK := $(shell command -v $(POETRY) 2> /dev/null)

.PHONY: install
install: $(INSTALL_STAMP)

$(INSTALL_STAMP): $(PYPROJECT_TOML) $(POETRY_LOCK)
	@if [ -z "$(POETRY_CHECK)" ]; then \
		echo "Poetry could not be found. See https://python-poetry.org/docs/"; \
		exit 2; \
	fi
	$(POETRY) install --no-root
	# Create an empty install stamp file to indicate that dependencies have been installed
	touch $(INSTALL_STAMP)

.PHONY: check
check: $(INSTALL_STAMP)
	# Run ruff to check for linting issues in the scripts directory
	$(POETRY) run ruff check $(SCRIPT_DIR)
	# Run ruff to check the formatting
	$(POETRY) run ruff format --check $(SCRIPT_DIR)
	# Run bandit to check for security issues
	$(POETRY) run bandit --quiet -r -c $(PYPROJECT_TOML) $(SCRIPT_DIR)
	# Run mypy to check for type issues
	$(POETRY) run mypy --config-file=$(PYPROJECT_TOML) $(SCRIPT_DIR)

.PHONY: format
format: $(INSTALL_STAMP)
	# Run ruff to automatically fix linting issues
	$(POETRY) run ruff check --fix $(SCRIPT_DIR)
	# Run ruff to format the scripts
	$(POETRY) run ruff format $(SCRIPT_DIR)

.PHONY: clean
clean:
	rm -f $(INSTALL_STAMP)
