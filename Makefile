.PHONY: validate validate-docker clean-junk

# Standard local validation entrypoint. It prefers the repository devcontainer
# image and falls back to the host only when Docker is unavailable.
validate:
	@./scripts/validate_ci_local.sh

validate-docker:
	@./scripts/validate_ci_local.sh --docker

clean-junk:
	@find . -type f \( -name '.DS_Store' -o -name '._*' -o -name 'Thumbs.db' \) ! -path './.git/*' -delete
	@find . -type d \( -name '__pycache__' -o -name '.pytest_cache' -o -name '.ruff_cache' -o -name '.ipynb_checkpoints' \) ! -path './.git/*' -prune -exec rm -rf {} +
