# Changelog

## v2.0.0

### Upgrade Notes

- Direct instantiation like `UserUUID()` no longer generates new UUIDs
  - Use `UserUUID.factory()` for random generation
  - Use `UserUUID(factory_uuid)` to wrap existing UUID instances
  - Version-specific factory methods accept their required parameters:
    - PUUIDv1/v6: node, clock_seq
    - PUUIDv3/v5: namespace, name
    - PUUIDv8: a, b, c
    - PUUIDv4/v7: no parameters
- The specialization syntax (`UserUUID = PUUIDv4[Literal["user"]]`) is no longer supported. Instead write `class UserUUID(PUUIDv4[Literal["user"]]): ...`. The [rationale behind this change](./limitations_and_design_choices.md).

### Added

- PUUID is now compatible for use in FastAPI using Pydantic models.
- `isinstance` checks and `case` clauses are correctly understood by major type checkers.

## v1.2.0

### Upgrade Notes

- **SQLAlchemy integration:** Make sure to remove the `prefix_length` argument at class instantiation.

### Changed

- **Remove prefix_length:** The prefix length is automatically derived from the PUUID class for the SQLAlchemy integration.

## v1.1.0

### Upgrade Notes

- **Empty prefix strings are now disallowed:** Attempting specialization with an empty string literal e.g. `class UserUUID(PUUIDv4[Literal[""]]):` now raises a `PUUIDError`
- **Prefer the new specialization syntax; the old `_prefix` pattern is discouraged.**
  - Recommended (v1.1.0+): `UserUUID = PUUIDv4[Literal["user"]]`
  - Discouraged (v1.0.0 style): `class UserUUID(PUUIDv4[Literal["user"]]): _prefix = "user"`
  - The old pattern is still supported for backwards compatibility, but it can silently drift (e.g. `_prefix` not matching the `Literal[...]`), using `class UserUUID(PUUIDv4[Literal["user"]])` is fine, but the `_prefix` is no longer necessary
- **Pydantic is now optional.** If you rely on pydantic integration, install pUUID with:
  - `pip install 'pUUID[pydantic]'`
- **Base class rename:** `PUUID` was renamed to `PUUIDBase`.
  - For backwards compatibility, `puuid.PUUID` is still available as an alias of `PUUIDBase`.

### Added

- **Dynamic Type Specialization:** Support for creating prefixed UUID classes directly via subscripting, e.g., `UserUUID = PUUIDv4[Literal["user"]]`.
- **Backward Compatibility Layer:** Added an alias for `PUUIDBase` as `PUUID` to maintain compatibility with v1.0.0 inheritance patterns.

### Changed

- **Renamed Base Class:** `PUUID` is now `PUUIDBase` to better reflect its role as a generic abstract base.
- **SQLAlchemy Improvements:** `SqlPUUID` is now generic, allowing better type-hinting of mapped columns.

## v1.0.0

- Initial release.
