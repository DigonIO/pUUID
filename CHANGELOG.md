# Changelog

## v1.1.0

### Upgrade Notes

- **Prefer the new specialization syntax; the old `_prefix` pattern is discouraged.**
  - Recommended (v1.1.0+): `UserUUID = PUUIDv4[Literal["user"]]`
  - Discouraged (v1.0.0 style): `class UserUUID(PUUIDv4[Literal["user"]]): _prefix = "user"`
  - The old pattern is still supported for backwards compatibility, but it can silently drift (e.g. `_prefix` not matching the `Literal[...]`), using `class UserUUID(PUUIDv4[Literal["user"]])` is fine, but the `_prefix` is no longer necessary
- **Pydantic is now optional.** If you rely on pydantic integration, install pUUID with:
  - `pip install 'pUUID[pydantic]'`
- **Base class rename:** `PUUID` was renamed to `PUUIDBase`.
  - For backwards compatibility, `puuid.PUUID` is still available as an alias of `PUUIDBase`.

### Added

- **Dynamic Type Specialization**: Support for creating prefixed UUID classes directly via subscripting, e.g., `UserUUID = PUUIDv4[Literal["user"]]`.
- **Backward Compatibility Layer**: Added an alias for `PUUIDBase` as `PUUID` to maintain compatibility with v1.0.0 inheritance patterns.

### Changed

- **Renamed Base Class**: `PUUID` is now `PUUIDBase` to better reflect its role as a generic abstract base.
- **SQLAlchemy Improvements**: `SqlPUUID` is now generic, allowing better type-hinting of mapped columns.

## v1.0.0

- Initial release.
