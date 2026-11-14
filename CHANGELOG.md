# Changelog

All notable changes to pyOFSC (the `ofsc` package on PyPI) are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).
Entries before 2.28.0 were reconstructed from the git tags, GitHub releases, pull requests
and PyPI uploads; 1.x releases carry only brief notes.

## [2.28.0] - 2026-11-13

### Added

- Added the activity custom actions to the async client — `start_prework`, `reopen_activity`, `delay_activity`, `cancel_activity`, `start_activity`, `enroute_activity`, `stop_travel`, `suspend_activity`, `complete_activity` and `notdone_activity`, each returning the updated `Activity` — plus `where_is_my_tech` (#123)
- Added the resource custom actions to the async client — `activate_route`, `deactivate_route`, `find_nearby_activities`, `bulk_update_resource_inventories`, `find_matching_resources`, `find_urgent_resources`, `set_positions`, `get_last_known_positions` and `get_resources_in_area` (#119)
- Added service requests to the async client — `create_service_request`, `get_service_request` and `get_service_request_property` (#127)

### Fixed

- Allowed everyday work-schedule recurrences without `recurEvery`, so one such item no longer fails the whole `get_resource_workschedules()` response (#218)

## [2.27.3] - 2026-11-13

### Fixed

- Fixed validation of activity types without a display name in `get_activity_types()` and `get_activity_type()` (#208, #215)
- Fixed inventory type translations dropping `unitOfMeasurement`, so writing an inventory type back no longer fails with a 400 (#211, #216)

## [2.27.2] - 2026-10-18

### Changed

- Changed CI to the advanced CodeQL setup and bumped pyjwt, urllib3 and GitHub Actions dependencies (#201, #202, #204, #205, #206)

## [2.27.1] - 2026-10-18

### Added

- Added a manually triggered workflow to publish the package to PyPI (#200)

### Changed

- Changed CI workflows to pin actions to commit SHAs and use read-only default token permissions (#203)
- Changed `SECURITY.md` to point to private vulnerability reporting and bumped urllib3 to 2.8.0 (#203)

## [2.27.0] - 2026-10-18

### Added

- Added `core.get_daily_extract_file_stream()` to stream daily extract downloads in the sync client (#160, #195)
- Added streaming daily extract downloads to the async client (#161, #197)
- Added async core search, move, bulk update and paginated collection helpers in place of `NotImplementedError` stubs (#151, #197)

### Changed

- Bumped runtime and development dependencies, including requests 2.33.0, cryptography 48.0.1 and pyjwt 2.13.0 (#159, #162, #164, #166, #179, #180)

### Fixed

- Fixed generic sync calls dropping additional headers (#197)
- Fixed `Property` validation rejecting an explicit `gui: null` returned by the API (#169, #177)
- Fixed `BulkUpdateWarning.message` to accept the string warning text OFS returns (#178, #181)
- Fixed capacity categories without a `name` failing validation on reads and updates (#189, #191)
- Fixed async write helpers sending snake_case keys instead of API aliases, e.g. in `create_or_replace_inventory_type` (#188, #190)

## [2.26.2] - 2026-05-31

### Added

- Added `HTTPClientConfig` to tune the async transport (concurrency, timeout, retries, proxy) via `AsyncOFSC(http_config=...)` (#170, #171)

### Changed

- Changed `CapacityCategory.workSkills` and `workSkillGroups` from `ItemList` to plain lists of dedicated models (#175, #176)
- Bumped the cryptography development dependency to 46.0.7 (#165)

### Fixed

- Fixed `CapacityCategory` dropping nested work skill fields such as `ratio`, `startDate` and `links` (#175, #176)

## [2.26.1] - 2026-05-27

### Changed

- Changed the `Recurrence` and `InventoryType` models to remove Pydantic deprecation warnings (#172)
- Bumped dependencies, including urllib3 2.7.0 and idna 3.15 (#167, #168, #172)

## [2.25.0] - 2026-03-05

### Added

- Added async generators `metadata.get_all_workzones()` and `core.get_all_resources()` that paginate lazily (#112, #158)

### Changed

- Changed the async capacity module to share CSV-parameter helpers, reducing duplication (#152)
- Changed the release workflow to create tags idempotently (#157)

## [2.24.3] - 2026-03-05

### Changed

- Changed the minimum supported Python to 3.13; this is the first PyPI release with that requirement, see 2.24.2 (breaking)
- Changed all async modules to share a common `AsyncClientBase` with generic HTTP helpers (#116, #148)
- Changed the release workflow to publish to PyPI as part of the release job (#155)

### Fixed

- Fixed missing URL encoding of labels in async `get_property`, `get_workzone`, `create_or_replace_property` and `update_property` (#116)
- Fixed inconsistent removal of `links` from async metadata responses (#116)

## [2.24.2] - 2026-03-05

- Tagged but not published on PyPI.

### Changed

- Changed the minimum supported Python from `~=3.11.0` to `>=3.13` (breaking) (#154)
- Changed dependency constraints to drop upper-bound pins and raise minimums, including Pydantic 2.12.5 (#154)

### Removed

- Removed the unused `pyarmor` development dependency (#154)

### Fixed

- Fixed a Pydantic deprecation warning when building capacity request parameters (#154)

## [2.24.1] - 2026-03-05

### Added

- Added optional request/response logging to the async client via `AsyncOFSC(enable_logging=True)` (#110, #153)

### Changed

- Changed library code to use named loggers and downgraded pagination logging from INFO to DEBUG (#153)

### Fixed

- Fixed async core and OAuth modules failing cryptically when `baseUrl` is unset; they now raise `ValueError` (#150)

### Security

- Removed a `print()` that wrote the OAuth bearer token to stdout (#153)

## [2.24.0] - 2026-03-04

### Added

- Added the async Core API for activities, resources, users, inventories, events, subscriptions and daily extracts (#118, #120, #122, #126)
- Added async multiday segments and resource file property methods (#139, #140)
- Added 22 async Metadata write methods and async capacity area sub-resources (#137, #138)
- Added the async Capacity API, including `get_available_capacity()` and `get_quota()` (#128)
- Added the async Statistics API GET and PATCH methods (#141, #142)
- Added OAuth token retrieval and Bearer token authentication to the async client (#146)

### Changed

- Changed the metadata Pydantic models after an audit of their fields and serialization (#149)
- Bumped cryptography to 46.0.5, requests to 2.32.4 and urllib3 to 2.6.3 (#134, #135, #136)

### Fixed

- Fixed an OAuth token caching bug affecting async capacity requests (#128)
- Fixed missing required parameters in async `get_calendars()`, `get_resource_assistants()` and `get_resource_plans()` (#147)

## [2.21.0] - 2025-12-29

### Added

- Added async Metadata GET methods for activity types and groups, properties, time slots, organizations and more (#109, #113)
- Added async Metadata methods for applications, capacity areas and categories, forms, map layers, plugins and shifts (#115)
- Added async work skill, work skill group and routing plan methods, including create, replace and delete (#105, #108, #115)
- Added custom exception types for the async client (#111, #113)
- Added HTTP/2 support to the async client (#114)

### Fixed

- Fixed `Property` validation rejecting the `attachments` GUI type (#114)

## [2.19.0] - 2025-12-23

### Added

- Added `AsyncOFSC`, an httpx-based async client, starting with workzone methods (#86, #89)

## [2.18.1] - 2025-12-12

### Added

- Added `get_workzone()` to the Metadata API (#85)

## [2.18.0] - 2025-12-11

### Added

- Added `replace_workzone()` to the Metadata API (#83, #84)

## [2.17.0] - 2025-10-28

### Added

- Added routing profile and routing plan models and methods, including plan export and import (#78, #79)
- Added `get_resources()` to list resources with pagination, field selection, filters and expansions (#81, #82)

## [2.15.0] - 2025-10-01

### Added

- Added `delete_activity()` to the Core API (#75, #77)

## [2.14.1] - 2025-06-25

### Fixed

- Fixed `getAvailableCapacity()` not returning all response fields, and added quota models (#71, #72)

## [2.14.0] - 2025-06-25

### Added

- Added the `OFSCapacity` module with `getAvailableCapacity()` and `getQuota()` (#69, #70)

### Changed

- Changed `getAvailableCapacity()` to take individual parameters instead of a `CapacityRequest` object (breaking) (#70)

## [2.13.0] - 2025-06-25

### Changed

- Changed package management from Poetry to uv (#65, #66)
- Changed the repository docs by adding CONTRIBUTING.md, SECURITY.md and issue templates (#61, #62)

## [2.12.3] - 2025-05-13

### Fixed

- Fixed the type of `Application.resourcesToAllow`, which made `get_applications()` fail validation (#59, #60)

## [2.12.2] - 2025-05-11

### Added

- Added models for daily extract folders and files (#58)

### Changed

- Bumped cryptography to 44.0.1 (#49)

### Fixed

- Fixed `get_daily_extract_file()` to request and return the file content (#58)

## [2.12.1] - 2025-04-18

### Removed

- Removed a debug `print()` of every API response and an unused import (#56, #57)

## [2.12.0] - 2025-04-08

### Added

- Added resource location methods to list, create and delete locations and to get and set assigned locations (#55)

## [2.11.0] - 2025-03-24

### Changed

- Changed `get_all_activities()` to keyword-only arguments with `date` defaults, returning `OFSResponseList[Activity]` (breaking) (#54)

## [2.10.0] - 2025-03-19

### Added

- Added a generic `call()` method to `OFSApi` for arbitrary API requests (#52, #53)

## [2.9.0] - 2025-03-19

### Added

- Added `get_resource_calendar()` and `CalendarView` models to read resource calendars (#51)

### Changed

- Changed responses to keep `links` when the target model defines a `links` field (#51)

## [2.8.0] - 2025-03-12

### Added

- Added `create_or_update_enumeration_value()` to the Metadata API (#50)

## [2.7.0] - 2025-02-10

### Added

- Added Applications and Organizations methods to the Metadata API (#45, #47, #48)
- Added bulk update methods for resource workzones, workskills and workschedules, and `get_enumeration_values()` (#45)

## [2.6.0] - 2025-01-13

- Published on PyPI without a tag or release notes.

## [2.5.0] - 2025-01-13

- Published on PyPI without a tag or release notes.

## [2.4.0] - 2024-12-17

- Published on PyPI without a tag or release notes.

## [2.3.0] - 2024-12-09

### Added

- Added methods to get, set and delete the users of a resource (#44)
- Added methods to read resource workschedules, inventories, assigned locations, workzones and workskills (#43, #44)

## [2.2.3] - 2024-12-02

- Published on PyPI without a tag or release notes.

## [2.2.1] - 2024-11-22

### Added

- Added `update_resource()` to the Core API (#42)

## [2.2.0] - 2024-11-22

- Published on PyPI without a tag or release notes.

## [2.1.0] - 2024-10-31

### Added

- Added work skill group methods to the Metadata API (#41)

## [2.0.5] - 2024-10-23

### Changed

- Changed pytest from a runtime to a development dependency

## [2.0.4] - 2024-10-23

### Changed

- Changed the library to Pydantic 2 (breaking) (#39)
- Bumped requests, urllib3, certifi and pydantic dependencies (#32, #34, #36, #37, #38)

## [1.20.3] - 2023-10-10

### Changed

- Bumped urllib3 to 1.26.17 (#30)

### Fixed

- Fixed the `root` argument of `OFSC` not being passed to the client configuration (#31)

## [1.20.2.1] - 2023-08-01

- Tagged but not published on PyPI.

### Changed

- Changed the PyPI publish workflow (#29)

## [1.20.2] - 2023-08-01

### Changed

- Changed the documentation with minor updates

## [1.20.1] - 2023-08-01

### Added

- Added `bulk_update()` to the Core API (#28)

## [1.20] - 2023-08-01

- Published on PyPI without a tag; the commit tagged v1.20.1 declares version 1.20.

## [1.19] - 2023-07-31

### Added

- Added OAuth2 token authentication as an alternative to basic authentication (#27)

### Changed

- Bumped requests and certifi (#23, #24, #25)

## [1.18.0.0] - 2022-12-03

### Added

- Added plugin import and property, resource type and resource creation methods (#21, #22)

## [1.17.4.4] - 2022-08-24

### Added

- Added `get_workzones()` to the Metadata API as part of a code rework (#20)

## [1.17.2] - 2022-08-07

### Added

- Added methods to read and replace work skill conditions (#19)

## [1.17.1] - 2022-08-06

### Changed

- Changed the README (#17, #18)

## [1.17] - 2022-08-06

### Added

- Added `core` and `metadata` sub-APIs on the client and work skill methods, as a start towards the 2.0 structure (#16)

## [1.16.5.2] - 2022-07-19

### Changed

- Changed the build tooling with a justfile and license metadata

## [1.16.5.1] - 2022-07-19

### Changed

- Changed the build system by completing the move to Poetry

## [1.16.5] - 2022-07-19

### Changed

- Changed the package metadata in `pyproject.toml`

## [1.16.4] - 2022-07-19

- Tagged but not published on PyPI.

### Changed

- Changed the package name in `pyproject.toml` to `ofsc`

## [1.16.3] - 2022-07-19

- Tagged but not published on PyPI.

### Changed

- Changed the build to Poetry with a `pyproject.toml` (#15)

## [1.16.2] - 2022-07-19

### Changed

- Changed publishing to a Poetry-based workflow

## [1.16.1] - 2022-07-19

### Changed

- Changed the README to document missing functions (#14)

## [1.16] - 2022-06-08

### Added

- Added methods to retrieve activity types (#13)

## [1.15] - 2022-02-02

### Added

- Added `get_properties()` and `get_file_properties()` (#12)

## [1.13.1] - 2021-08-15

### Changed

- Changed the packaging metadata in `setup.py` (release titled "Minor fixes")

## [1.13] - 2021-07-26

### Added

- Added `search_activities()` (#10)

## [1.11] - 2021-07-21

### Added

- Added `create_resource()` (#9)

## [1.10] - 2021-06-10

### Added

- Added functions to create and delete users

## [1.9] - 2021-04-27

### Added

- Added user management functions

## [1.8.1] - 2021-02-22

### Added

- Added read-only activity type group functions (#5)

## [1.8] - 2021-01-14

### Added

- Added an optional `baseUrl` parameter to the client, defaulting to `https://api.etadirect.com` (#4)

## [1.7] - 2020-08-27

### Added

- Added functions to retrieve capacity metadata (#3)

## [1.6.3] - 2020-04-03

### Fixed

- Fixed an error in `get_resource_descendants()` (#2)

## [1.6.2] - 2020-04-03

### Fixed

- Fixed an error in `get_resource_descendants()` (#1)

## [1.6.1] - 2020-02-25

### Added

- Added `get_resource_descendants()`

## [1.6.0] - 2019-11-19

### Added

- Added `get_resource_route()`

## [1.5.1] - 2019-11-19

### Fixed

- Fixed the package setup

## [1.5.0] - 2019-11-19

- Tagged but not published on PyPI.

### Added

- Added functions to handle resource details

## [1.4.0] - 2019-11-04

### Added

- Added a `response_type` option to get responses in different formats

## [1.3.3] - 2019-10-23

### Changed

- Changed `setup.py` to fix automated PyPI publishing

## [1.3.2] - 2019-10-23

- Tagged but not published on PyPI.

### Added

- Added a workflow to publish to PyPI

## [1.3.1] - 2019-10-23

### Added

- Added the package manifest and `ofsc/__init__.py`

## [1.3] - 2019-10-23

- First release published on PyPI (as `v1.3`), with an updated `setup.py` and a license file.

## [1.2] - 2019-10-23

- Tagged but not published on PyPI.

### Changed

- Changed `setup.py`

## [1.1] - 2019-10-23

- Tagged as both `1.1` and `v1.1`; not published on PyPI.

### Changed

- Changed `setup.py` and added `setup.cfg`

## [1.0] - 2019-10-23

- Tagged but not published on PyPI.

### Added

- Added the initial release of the library

[2.28.0]: https://github.com/btoron/pyOFSC/compare/v2.27.3...v2.28.0
[2.27.3]: https://github.com/btoron/pyOFSC/compare/v2.27.2...v2.27.3
[2.27.2]: https://github.com/btoron/pyOFSC/compare/v2.27.1...v2.27.2
[2.27.1]: https://github.com/btoron/pyOFSC/compare/v2.27...v2.27.1
[2.27.0]: https://github.com/btoron/pyOFSC/compare/v2.26.2...v2.27
[2.26.2]: https://github.com/btoron/pyOFSC/compare/v2.26.1...v2.26.2
[2.26.1]: https://github.com/btoron/pyOFSC/compare/v2.25.0...v2.26.1
[2.25.0]: https://github.com/btoron/pyOFSC/compare/v2.24.3...v2.25.0
[2.24.3]: https://github.com/btoron/pyOFSC/compare/v2.24.2...v2.24.3
[2.24.2]: https://github.com/btoron/pyOFSC/compare/v2.24.1...v2.24.2
[2.24.1]: https://github.com/btoron/pyOFSC/compare/v2.24.0...v2.24.1
[2.24.0]: https://github.com/btoron/pyOFSC/compare/v2.21.0...v2.24.0
[2.21.0]: https://github.com/btoron/pyOFSC/compare/v2.19...v2.21.0
[2.19.0]: https://github.com/btoron/pyOFSC/compare/v2.18.1...v2.19
[2.18.1]: https://github.com/btoron/pyOFSC/compare/v2.18...v2.18.1
[2.18.0]: https://github.com/btoron/pyOFSC/compare/v2.17...v2.18
[2.17.0]: https://github.com/btoron/pyOFSC/compare/v2.15...v2.17
[2.15.0]: https://github.com/btoron/pyOFSC/compare/v2.14.1...v2.15
[2.14.1]: https://github.com/btoron/pyOFSC/compare/v2.14...v2.14.1
[2.14.0]: https://github.com/btoron/pyOFSC/compare/v2.13...v2.14
[2.13.0]: https://github.com/btoron/pyOFSC/compare/v2.12.3...v2.13
[2.12.3]: https://github.com/btoron/pyOFSC/compare/v2.12.2...v2.12.3
[2.12.2]: https://github.com/btoron/pyOFSC/compare/v2.212.1...v2.12.2
[2.12.1]: https://github.com/btoron/pyOFSC/compare/v2.12...v2.212.1
[2.12.0]: https://github.com/btoron/pyOFSC/compare/v2.11...v2.12
[2.11.0]: https://github.com/btoron/pyOFSC/compare/v2.10...v2.11
[2.10.0]: https://github.com/btoron/pyOFSC/compare/v2.9...v2.10
[2.9.0]: https://github.com/btoron/pyOFSC/compare/v2.8...v2.9
[2.8.0]: https://github.com/btoron/pyOFSC/compare/v2.7...v2.8
[2.7.0]: https://github.com/btoron/pyOFSC/compare/v2.3...v2.7
[2.6.0]: https://pypi.org/project/ofsc/2.6.0/
[2.5.0]: https://pypi.org/project/ofsc/2.5.0/
[2.4.0]: https://pypi.org/project/ofsc/2.4.0/
[2.3.0]: https://github.com/btoron/pyOFSC/compare/v2.2...v2.3
[2.2.3]: https://pypi.org/project/ofsc/2.2.3/
[2.2.1]: https://github.com/btoron/pyOFSC/compare/v2.1...v2.2
[2.2.0]: https://pypi.org/project/ofsc/2.2.0/
[2.1.0]: https://github.com/btoron/pyOFSC/compare/v2.0.5...v2.1
[2.0.5]: https://github.com/btoron/pyOFSC/compare/v2.0...v2.0.5
[2.0.4]: https://github.com/btoron/pyOFSC/compare/v1.20.3...v2.0
[1.20.3]: https://github.com/btoron/pyOFSC/compare/v1.20.2.1...v1.20.3
[1.20.2.1]: https://github.com/btoron/pyOFSC/compare/v1.20.2...v1.20.2.1
[1.20.2]: https://github.com/btoron/pyOFSC/compare/v1.20.1...v1.20.2
[1.20.1]: https://github.com/btoron/pyOFSC/compare/v1.19...v1.20.1
[1.20]: https://pypi.org/project/ofsc/1.20/
[1.19]: https://github.com/btoron/pyOFSC/compare/v1.18.0.0...v1.19
[1.18.0.0]: https://github.com/btoron/pyOFSC/compare/v1.17.4.4...v1.18.0.0
[1.17.4.4]: https://github.com/btoron/pyOFSC/compare/v1.17.2...v1.17.4.4
[1.17.2]: https://github.com/btoron/pyOFSC/compare/v1.17.1...v1.17.2
[1.17.1]: https://github.com/btoron/pyOFSC/compare/v1.17...v1.17.1
[1.17]: https://github.com/btoron/pyOFSC/compare/v1.16.5.2...v1.17
[1.16.5.2]: https://github.com/btoron/pyOFSC/compare/v1.16.5.1...v1.16.5.2
[1.16.5.1]: https://github.com/btoron/pyOFSC/compare/v1.16.5...v1.16.5.1
[1.16.5]: https://github.com/btoron/pyOFSC/compare/v1.16.4...v1.16.5
[1.16.4]: https://github.com/btoron/pyOFSC/compare/v1.16.3...v1.16.4
[1.16.3]: https://github.com/btoron/pyOFSC/compare/v1.16.2...v1.16.3
[1.16.2]: https://github.com/btoron/pyOFSC/compare/v1.16.1...v1.16.2
[1.16.1]: https://github.com/btoron/pyOFSC/compare/v1.16...v1.16.1
[1.16]: https://github.com/btoron/pyOFSC/compare/1.15...v1.16
[1.15]: https://github.com/btoron/pyOFSC/compare/v1.13.1...1.15
[1.13.1]: https://github.com/btoron/pyOFSC/compare/v1.13...v1.13.1
[1.13]: https://github.com/btoron/pyOFSC/compare/v1.11...v1.13
[1.11]: https://github.com/btoron/pyOFSC/compare/v1.10...v1.11
[1.10]: https://github.com/btoron/pyOFSC/compare/v1.9...v1.10
[1.9]: https://github.com/btoron/pyOFSC/compare/v1.8.1...v1.9
[1.8.1]: https://github.com/btoron/pyOFSC/compare/v1.8...v1.8.1
[1.8]: https://github.com/btoron/pyOFSC/compare/v1.7...v1.8
[1.7]: https://github.com/btoron/pyOFSC/compare/1.6.3...v1.7
[1.6.3]: https://github.com/btoron/pyOFSC/compare/1.6.2...1.6.3
[1.6.2]: https://github.com/btoron/pyOFSC/compare/1.6.1...1.6.2
[1.6.1]: https://github.com/btoron/pyOFSC/compare/1.6.0...1.6.1
[1.6.0]: https://github.com/btoron/pyOFSC/compare/v1.5.1...1.6.0
[1.5.1]: https://github.com/btoron/pyOFSC/compare/v1.5.0...v1.5.1
[1.5.0]: https://github.com/btoron/pyOFSC/compare/v1.4.0...v1.5.0
[1.4.0]: https://github.com/btoron/pyOFSC/compare/v1.3.3...v1.4.0
[1.3.3]: https://github.com/btoron/pyOFSC/compare/v1.3.2...v1.3.3
[1.3.2]: https://github.com/btoron/pyOFSC/compare/v1.3.1...v1.3.2
[1.3.1]: https://github.com/btoron/pyOFSC/compare/v1.3...v1.3.1
[1.3]: https://github.com/btoron/pyOFSC/compare/v1.2...v1.3
[1.2]: https://github.com/btoron/pyOFSC/compare/v1.1...v1.2
[1.1]: https://github.com/btoron/pyOFSC/compare/1.0...v1.1
[1.0]: https://github.com/btoron/pyOFSC/releases/tag/1.0
