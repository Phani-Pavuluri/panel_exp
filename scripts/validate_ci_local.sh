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
    --volume "${repo_root}:/workspace/panel_exp-source:ro" \
    --workdir /workspace/panel_exp \
    "${image}" \
    bash -lc '
      set -euo pipefail
      tar --exclude=.git --exclude=.venv -C /workspace/panel_exp-source -cf - . | tar -C /workspace/panel_exp -xf -
      export POETRY_VIRTUALENVS_IN_PROJECT=false
      export POETRY_CACHE_DIR=/tmp/pypoetry-cache
      export POETRY_VIRTUALENVS_PATH=/tmp/pypoetry-venvs
      echo "[validate-docker] Using isolated Poetry virtualenv outside mounted repo"
      echo "[validate-docker] POETRY_VIRTUALENVS_IN_PROJECT=${POETRY_VIRTUALENVS_IN_PROJECT}"
      echo "[validate-docker] POETRY_VIRTUALENVS_PATH=${POETRY_VIRTUALENVS_PATH}"
      python -m pip install --disable-pip-version-check "poetry==1.8.5"
      poetry install --with dev --no-interaction
      poetry run python -m pytest tests/ -q
    '
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
