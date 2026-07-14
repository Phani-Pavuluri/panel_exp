#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
image="panel-exp-validation:local"
mode="${1:-auto}"

run_checks() {
  if command -v python3 >/dev/null 2>&1; then
    python3 -m pytest tests/ -q
  else
    python -m pytest tests/ -q
  fi
}

docker_is_available() {
  command -v docker >/dev/null 2>&1 && docker info >/dev/null 2>&1
}

run_docker() {
  docker build --tag "${image}" --file "${repo_root}/.devcontainer/Dockerfile" "${repo_root}"
  docker run --rm \
    --volume "${repo_root}:/workspace/panel_exp" \
    --tmpfs /workspace/panel_exp/.venv \
    --workdir /workspace/panel_exp \
    "${image}" \
    bash -lc "python -m pip install --disable-pip-version-check 'poetry==1.8.5' && poetry config virtualenvs.create false && poetry install --with dev --no-interaction && poetry run pytest tests/ -q"
}

case "${mode}" in
  --docker)
    if ! docker_is_available; then
      echo "Docker is required for make validate-docker but is not available." >&2
      exit 1
    fi
    run_docker
    ;;
  auto)
    if docker_is_available; then
      echo "Docker is available; validating with the repository devcontainer image."
      run_docker
    else
      echo "Docker is unavailable; falling back to the host Python environment." >&2
      cd "${repo_root}"
      run_checks
    fi
    ;;
  *)
    echo "Usage: $0 [--docker]" >&2
    exit 2
    ;;
esac
