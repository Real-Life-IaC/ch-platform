SHELL=/bin/bash

.DEFAULT_GOAL := help

.PHONY: help
help: ## Shows this help text
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.PHONY: init
init: clean install checkov test ## Clean the environment and install all project dependencies

.PHONY: clean
clean: ## Removes project virtual env and untracked files
	rm -rf .venv cdk.out build dist **/*.egg-info .pytest_cache node_modules .coverage
	poetry env remove --all

.PHONY: install
install: ## Install the project dependencies using Poetry.
	poetry install --with lint,test,checkov
	poetry run pre-commit install --hook-type pre-commit --hook-type commit-msg --hook-type pre-push

.PHONY: update
update: ## Update the project dependencies using Poetry.
	poetry update --with lint,test,checkov

.PHONY: test
test: ## Run tests
	poetry run python -m pytest

.PHONY: lint
lint: ## Apply linters to all files
	poetry run pre-commit run --all-files

.PHONY: synth
synth: ## Synthetize all Cdk stacks
	poetry run cdk synth

.PHONY: checkov
checkov: synth ## Run Checkov against IAC code
	poetry run checkov --config-file .checkov --baseline .checkov.baseline

.PHONY: checkov-baseline
checkov-baseline: synth ## Run checkov and create a new baseline for future checks
	poetry run checkov --config-file .checkov --create-baseline --soft-fail
	mv cdk.out/.checkov.baseline .checkov.baseline

.PHONY: snapshot-update
snapshot-update: ## Run tests and update the snapshots baseline
	poetry run python -m pytest --snapshot-update
