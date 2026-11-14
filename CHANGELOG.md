# Changelog

All notable changes to pyOFSC (the `ofsc` package on PyPI) are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).
Releases before 2.28.0 are not listed here; see the
[tags](https://github.com/btoron/pyOFSC/tags) and their release pull requests.

## [Unreleased]

### Added

- Added the activity custom actions to the async client — `start_prework`, `reopen_activity`, `delay_activity`, `cancel_activity`, `start_activity`, `enroute_activity`, `stop_travel`, `suspend_activity`, `complete_activity` and `notdone_activity`, each returning the updated `Activity` — plus `where_is_my_tech` (#123)

## [2.28.0] - 2026-11-13

### Fixed

- Allowed everyday work-schedule recurrences without `recurEvery`, so one such item no longer fails the whole `get_resource_workschedules()` response (#218)

[Unreleased]: https://github.com/btoron/pyOFSC/compare/v2.28.0...HEAD
[2.28.0]: https://github.com/btoron/pyOFSC/compare/v2.27.3...v2.28.0
