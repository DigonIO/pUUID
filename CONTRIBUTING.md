# HowTo: Contribute to pUUID

## Development setup

Install dependencies

```console
uv sync --all-groups
```

## Formatting

```console
uv run black ./src ./tests
uv run isort ./src ./tests
```

## Testing

### Standard tests

```console
uv run pytest --cov=src/puuid/ tests
```

## Visual coverage report

Generate the html coverage report. The command creates a folder `htmlcov` with an `index.html` as landing page.

```console
uv run coverage html
```

## Static analysis

Run mypy with:

```console
uv run mypy src
```

Run ruff with:

```console
uv run ruff check src
```
