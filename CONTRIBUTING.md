# Contributing

## Setup

This project uses [uv](https://docs.astral.sh/uv/). Install the dependencies and the pre-commit hooks with:

```bash
uv sync
uv run pre-commit install
```

## Checks

CI runs these on every supported Python version, so run them before opening a PR:

```bash
uv run ruff check
uv run ruff format --check
uv run mypy vivintpy tests
uv run pytest
```

## Z-Wave device database

A workflow updates this every week and opens a PR, so you don't need to do this for a normal change. To update it yourself, run:

```bash
uv run python script/gen_zjs_device_config_db.py
```

## Releasing

Publishing a GitHub release tags the commit, and the tag starts a workflow that builds the package, smoke tests it and publishes it to PyPI. The version comes from the tag, so nothing needs changing in the code.

Check that the Publish python package workflow succeeded, because a release can appear on GitHub without reaching PyPI. If the run failed, re-run it from the Actions tab. If it never started, delete the tag from GitHub and push it again, as publishing the release again won't start it:

```bash
git push origin --delete <tag>
git push origin <tag>
```

To check the package builds locally, run:

```bash
uv build
```
