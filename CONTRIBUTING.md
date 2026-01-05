# HowTo: Contribute to pUUID

## Development setup

Install dependencies

```bash
uv sync --all-groups
```

## Formatting

```bash
uv run black ./src ./tests
uv run isort ./src ./tests
```

## Testing

### Standard tests

```bash
uv run pytest --cov=src/puuid/ tests
```

## Visual coverage report

Generate the html coverage report. The command creates a folder `htmlcov` with an `index.html` as landing page.

```bash
uv run coverage html
```

## Static analysis

Run static analysis with:

```bash
uv run ruff check src
uv run mypy src
uv run basedpyright src
```

As the development is currently experimental and focussed on the `context_enrichers` module and getting bdd right, we are ignoring the noisy errors in the remaining modules under `src/llm_dispatch` for now.

## Style Guide

### Type Annotations

- Use Python 3.14 type hints everywhere (including tests).
- Try to keep the types as narrow as possible
- Avoid `Any`, `TypeVar` (unless truly needed for variance), `cast`, and `type: ignore` where possible.
- Prefer `collections.abc` (`Iterable`, `Mapping`, `Callable`, …) over `typing` aliases.
- avoid using `object` for annotations
- avoid using `cast` for annotations
- Try to use `StrEnum` or `Literal` types where possible and limit `str` usage if the content can be known in advance.
- the `__init__` method of a class be annotated with types for all arguments (except `self`) and in addition annotate the return type `None`
- `dict` is a generic type and requires two type arguments. In most cases a `TypedDict` should be preferred over using `dict`. As `dict` itself is type invariant, it should generally be avoided as an input argument for a function - `collections.abc.Mapping` (being covariant) is a much better fit.
- No need do `from __future__ import annotations`, we are already on the newest stable 3.14 release, to the contrary - using this import will eagerly evaluate type annotations and makes forward references awkward (they'd require strings for the types)
- Do not use strings for types, they are lazily evaluated in 3.14, which allows us to use the classes directly (even with forward declarations)
- Avoid using `typing.TypeGuard`, `typing.TypeIs` (introduced in 3.13) is almost always a superior drop-in replacement

### Code Style

- Avoid nested function definitions except when necessary (e.g. decorators).
- Use full import paths within the package (e.g. `from llm_dispatch.context_enrichers.snippets import SnippetMeta`).
- Use `pathlib.Path` instead of `os.path`.
- Do not concatenate strings with `+`; use f-strings instead.
- Avoid hard coding class names as string for the `__repr__` and `__str__` methods. Extract the string from the class directly, so if we ever decide to rename the class we do not forget about strings left somewhere.
- Try to keep the body of functions manageable in size (target below 20 lines), you should separate logical blocks out into helper functions (even if they are only used once) to achieve this.
- Avoid reassigning to the same variable multiple times. It is ok to update a collection (e.g. list), but full on reassignments should be kept to a minimum.
