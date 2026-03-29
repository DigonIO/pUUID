# TODO

## Task IDs

- `xxxx?` Optional
- `xxxx.` Normal
- `xxxx!` Critical

Next ID: `9`

## Open Tasks

- `8!` Match/Case and isinstance should work as specified (type checker and runtime)
- `7!` While `pydantic` "understands" `puuid`, FastAPI does not. We need to define `__get_pydantic_json_schema__`.
- `6!` It should not be possible to instanciate ill defined specializations (e.g. `PUUIDv4[str]`, `PUUID[str]` in runtime)
- `5.` Implement human-friendly `__repr__`

## Done Tasks

- `4.` Compute `to_string()` on demand to reduce overhead during `__init__` + add caching
- `3.` Disallow empty prefix (`Literal[""]`)
- `2.` Add `Upgrade Notes` to `CONTRIBUTING.md`
- `1.` Make `pydantic` an optional dependency
