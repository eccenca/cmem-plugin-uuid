# Change Log

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/) and this project adheres to [Semantic Versioning](https://semver.org/)

## [3.0.0b1] 2026-06-19

### Changed

- Update template to 8.4.1
- UUID8 plugin: three optional custom data fields `a` (48-bit), `b` (12-bit) and `c` (62-bit) per RFC 9562 §5.8. Missing fields are filled with random data.

### Breaking Change

- UUID8 output is no longer time-ordered. Use UUIDv7 if sortability by creation time is required.

## [2.0.0] 2025-10-16

### Changed

- Update of dependencies and template
- validation of python 3.13 compatibility

### Breaking Change

- Requires python 3.13 now (>= CMEM 25.3.x)

## [1.1.0] 2025-02-13

### Changed

- Update template to 7.1.0
- Output empty value instead of throwing an error if no input is given for plugins that require an input value 


## [1.0.0] 2024-02-12

### Added

- initial version

