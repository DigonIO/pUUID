# Changelog

## v1.1.0

### Added

- **Dynamic Type Specialization**: Support for creating prefixed UUID classes directly via subscripting, e.g., `UserUUID = PUUIDv4[Literal["user"]]`.
- **Backward Compatibility Layer**: Added an alias for `PUUIDBase` as `PUUID` to maintain compatibility with v1.0.0 inheritance patterns.

### Changed

- **Renamed Base Class**: `PUUID` is now `PUUIDBase` to better reflect its role as a generic abstract base.
- **SQLAlchemy Improvements**: `SqlPUUID` is now generic, allowing better type-hinting of mapped columns.

## v1.0.0

- Initial release.
