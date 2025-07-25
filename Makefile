VENV_FOLDER=.venv

ifeq (, $(shell which uv ))
  $(error "[ERROR] The 'uv' command is missing from your PATH. Install it from: https://docs.astral.sh/uv/getting-started/installation/")
endif

.PHONY: help
help: ## Display this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.PHONY: install
install: $(VENV_FOLDER)/bin/buildout .git/hooks/pre-commit ## Install development environment
	$(VENV_FOLDER)/bin/buildout

.PHONY: start
start: bin/instance .git/hooks/pre-commit ## Start the instance
	bin/instance fg

.PHONY: cleanall
cleanall: ## Clean development environment
	rm -fr .git/hooks/pre-commit .installed.cfg .mr.developer.cfg .venv bin buildout.cfg devel develop-eggs downloads eggs htmlcov include lib lib64 local parts pyvenv.cfg

.PHONY: upgrade-steps
upgrade-steps: ## Run upgrade steps
	bin/instance -O Plone run scripts/run_portal_upgrades.py

.PHONY: lint
lint: ## Run pre-commit hooks
	uvx pre-commit run --all

.PHONY: fullrelease
fullrelease: ## Release package with zest.releaser fullrelease
	uvx --from zest.releaser fullrelease

.PHONY: test
test: bin/instance ## Test package
	bin/test

.PHONY: test-coverage
test-coverage: test ## Test package with coverage
	bin/test-coverage

.venv:
	@echo "Creating virtual environment with uv"
	uv venv

buildout.cfg:
	ln -fs dev.cfg buildout.cfg

$(VENV_FOLDER)/bin/buildout: .venv buildout.cfg
	@echo "Installing requirements with uv pip interface"
	uv pip install -r requirements.txt

bin/instance: $(VENV_FOLDER)/bin/buildout
	@echo "Bootstrapping environment with buildout"
	$(VENV_FOLDER)/bin/buildout

.git/hooks/pre-commit: .venv
	@echo "Installing pre-commit hooks"
	uvx pre-commit install
