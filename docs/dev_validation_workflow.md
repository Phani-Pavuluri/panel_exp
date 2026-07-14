# Local development validation

Run the repository-standard validation from the repository root:

```bash
make validate
```

## Environment selection

The repository provides a Python 3.11 devcontainer in `.devcontainer/`. There is
no root `Dockerfile`, Docker Compose configuration, or `justfile`.

`make validate` uses Docker and the devcontainer image when the Docker CLI and
daemon are available. It installs the Poetry version pinned by the devcontainer,
installs the locked development dependencies, and runs the full test suite. If
Docker is unavailable, it falls back to the same pytest invocation with the host
Python interpreter (whose environment must already contain the development
dependencies). Use `make validate-docker` when Docker must be required rather than
falling back.

## Validation payload and CI parity

The shared validation payload is:

```bash
python -m pytest tests/ -q
```

The container invokes this through Poetry after installing `poetry.lock`; the
host fallback invokes it directly and does not depend on host-local Poetry. This
is the full-suite test payload documented throughout the repository. There are
currently no files under `.github/workflows/`, so GitHub Actions defines neither
additional validation commands nor a Python-version matrix in this checkout.
Local validation is therefore only a partial CI equivalent: it verifies the
documented test suite on Python 3.11, while any future or externally configured
GitHub Actions checks remain the final authority.

## Cleanup

Remove ignored operating-system files and local Python/test caches with:

```bash
make clean-junk
```

The cleanup target does not remove validation archives or generated project
artifacts.
