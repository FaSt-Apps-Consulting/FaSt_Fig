# AGENTS.md

Agent knowledge base for the FaSt_Fig repository.

## Project

FaSt_Fig is a matplotlib wrapper providing a simple interface for fast plotting:
FFig class with presets/templates, DataFrame handling, subplot management, and
automatic resource cleanup via context manager. Pure-source package (no C
extensions), single import package `fast_fig/`.

- **Requires Python**: `>=3.12` (CI tests 3.12–3.14)
- **Runtime deps**: numpy, matplotlib, pandas, pyyaml (only 4 — stdlib packages
  are never listed as dependencies)
- **Version single source**: `version` in `pyproject.toml` (no `__version__` in code)
- **License**: MIT (`license = "MIT"` SPDX expression, PEP 639)

## Tooling

The project uses **uv** as the package manager (uv.lock is committed).

```bash
uv sync --locked          # reproducible install (also updates via `uv lock`)
uv run ruff check .       # lint (select = ALL, line-length 100)
uv run ruff format --check .  # formatting check
uv run pytest             # tests + coverage (via [tool.pytest.ini_options])
uv build                  # build sdist + wheel into dist/
```

Known test caveat: `tests/test_references.py` checksum tests fail on current
matplotlib (renderer drift). They are pre-existing and unrelated to packaging;
exclude with `uv run pytest -k "not references"` until reference images are
regenerated.

## CI

- **GitHub Actions** (source of truth):
  - `.github/workflows/python-package.yml` — lint + test matrix (3.12–3.14) on main pushes/PRs
  - `.github/workflows/publish-to-pypi.yml` — build, then publish to TestPyPI (main pushes) and PyPI (tag pushes), see Release Process
- **Codeberg Woodpecker** (`.woodpecker/lint.yaml`, `.woodpecker/test.yaml`) — mirrors the GitHub CI

## Release process (v0.8.x)

Releases are published automatically from GitHub Actions using **Trusted
Publishing (OIDC)** — no API tokens or secrets are used anywhere.

### One-time setup (already done)

- Trusted publishers registered on **pypi.org** (environment `pypi`) and
  **test.pypi.org** (environment `testpypi`, separate account). Both must use:
  owner `FaSt-Apps-Consulting`, repo `FaSt_Fig`, workflow **`publish-to-pypi.yml`**,
  matching environment name. Pending publishers become active after first use.
- GitHub Environments: `pypi` (required reviewers = manual approval gate) and
  `testpypi` (no approval).

### Steps

1. **Develop on `dev`**, then prepare the release in `dev`:
   - Bump `version` in `pyproject.toml` (e.g. `0.8.4`)
   - Add entry to `CHANGELOG.md` (`## [x.y.z] - YYYY-MM-DD` + bullet list)
   - `uv lock` to update uv.lock (it records the project's own version)
2. **Verify locally**:
   - `rm -rf dist/* && uv build` and inspect wheel metadata
   - `uv run ruff check .` and `uv run ruff format --check .`
   - `uv run pytest -k "not references"` (or full; reference failures known)
3. **Merge `dev` → `main` and push** — the publish workflow runs its build job
   and the `publish-to-testpypi` job (TestPyPI dry run of the exact artifacts).
4. **Tag the release — the PyPI trigger**:
   ```bash
   git tag v0.8.4 && git push origin v0.8.4
   ```
   The tag **must** start with `v` (workflow trigger is `tags: ["v*"]`).
   Skipping the tag is why PyPI stays unpublished after a main push.
5. **Approve the PyPI deployment**: the `publish-to-pypi` job requires manual
   approval (required reviewers on the `pypi` environment). In Actions →
   "Publish Python distribution to PyPI and TestPyPI" → Review deployments →
   approve.
6. **Verify**: `https://pypi.org/p/fast_fig` shows the new version with sdist +
   wheel and PEP 740 attestations; the publisher flips from pending to active.

### Troubleshooting

- `invalid-publisher` / "no corresponding publisher" → the trusted-publisher
  registration does not match the OIDC claims. Compare the claim output from
  the failing job (`workflow_ref`, `environment`, `repository_owner`) against
  the registered values. Typical mistakes: wrong workflow filename
  (`publish-to-testpypi.yml` vs `publish-to-pypi.yml`), wrong environment name,
  or registering on the wrong index (pypi.org vs test.pypi.org). Publishers
  cannot be edited — delete and re-add.
- Job "Waiting" → pending manual approval in the `pypi` environment.
- Deprecation warnings in workflow runs → GitHub Actions Node runtime bumps;
  action majors live in `.github/workflows/*.yml`.

## Build/packaging conventions (PyPA user guide compliant)

- `[build-system]` → `setuptools >= 77.0.3` / `setuptools.build_meta` (PEP 639)
- `license = "MIT"` + `license-files`, `[project.urls]` (Homepage/Repository/
  Issues/Changelog), requires-python without upper bound
- Classifiers: no `License ::` classifier (conflicts with `License-Expression`)
- Only 4 runtime dependencies; never add stdlib-shadowing packages
  (`logging`, `pathlib`, etc.) as dependencies
- `dist/` and `fast_fig.egg-info/` are gitignored build artifacts; clean
  `dist/` before building