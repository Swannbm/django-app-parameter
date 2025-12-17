# Changelog

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]

## [2.1.3] - 2025.11.15

### Fixed
* Context processor now passes global parameters to templates in their declared format instead of converting everything to strings
* Fixed Ruff linting errors

## [2.1.2] - 2025.11.15

### Changed
* Modernized README with concise quick start guide and feature overview
* Improved documentation structure with links to full documentation

## [2.1.1] - 2025.11.15

### Fixed
* Read the Docs build configuration: created `docs/requirements.txt` with Sphinx dependencies and simplified `.readthedocs.yaml` to properly support Poetry-based projects

## [2.1.0] - 2025.11.15

### Added
* Encryption support for parameters with `enable_cypher` field
* `dap_rotate_key` management command for rotating encryption keys (two-step process for safety)
* Persistent backup file for encryption keys (`dap_backup_key.json`)
* Parameter value history tracking: new `enable_history` field to track previous values with timestamps via `ParameterHistory` model (viewable in admin as read-only inline)
* Full documentation with Sphinx and ReadTheDocs hosting

### Changed
* Management commands renamed with `dap_` prefix to avoid conflicts: `load_param` → `dap_load`, `dump_param` → `dap_dump`
* Key rotation process redesigned: step 1 generates new key and backs up old one, step 2 applies rotation

## [2.0.0] - 2025.11.14

### Added
* Setter methods to programmatically update parameter values
* Parameter validators with built-in validation rules (min/max value, length, regex, etc.)
* `ParameterValidator` model to attach multiple validators to parameters
* Custom validators support via `DJANGO_APP_PARAMETER['validators']` setting
* Dynamic validator selection in Django admin with automatic form validation
* Validator support in `load_param` management command via JSON format (validators in JSON represent the final desired state)
* dump_param management command to export all parameters to JSON file
* Demo project for manual testing and development with example custom validators
* New parameter types:
  * URL (validated URL)
  * Email (validated email address)
  * List (comma-separated values)
  * Dict (JSON dictionary)
  * Path (file path)
  * Duration (time duration in seconds)
  * Percentage (0-100)
  * DateTime (ISO 8601 datetime)
  * Date (YYYY-MM-DD)
  * Time (HH:MM:SS)
* Full type hints coverage with Pyright
* Enhanced admin interface for managing setters and validators
* Custom admin template for parameter change form

### Changed
* Modernized development tooling: migrated from Black/Flake8 to Ruff
* Improved testing strategy with comprehensive test coverage
* Updated documentation with new features and usage examples
* Enhanced CONTRIBUTING.md with demo project instructions

### Fixed
* Migration for renaming DATE and TIME type codes to DAT and TIM (to avoid conflicts with new types)

## [1.1.3] - 2023.10.18

### Added
* Boolean type

### Fixed
* Avoid exception on incorrect parameter's type
* Missing migration

## [0.2.0] -

### Added
* Added get method on Parameter with autocasting
* Added a proxy class to access parameter through app_parameter.SLUG (like Django's settings)

## [0.1.3] - 2022-02-23

First public release.

### Added
* Add unit test
* Add use case in readme

### Changed
* Replace "-" by "_" in slug initialisation


