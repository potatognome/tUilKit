
# CHANGELOG

## [0.5.2] - 2025-12-28

### Added
- New test file `test_interfaces.py` for comprehensive testing of ConfigLoader, ColourManager, Logger, and FileSystem interfaces.

### Changed
- Updated `ConfigLoader.ensure_folders_exist` to create folders based on `LOG_FILES` paths instead of non-existent `MAKE_FOLDERS`.
- Removed broken code in `config.py` that referenced invalid config keys.

### Fixed
- ConfigLoader now properly handles folder creation for log files.

## [0.5.1] - 2025-12-27

### Added
- New colour key system with `!` prefixed keys (e.g., `!date`, `!time`, `!proc`) for improved readability and consistency.
- Support for foreground and background color combinations in `COLOUR_KEY` using `FG|BG` format (e.g., `GREEN|BLACK`).
- `interpret_codes` method in `ColourManager` to interpret colour codes in text strings using `{colour}` syntax.
- Support for multiple log files in all logging methods by changing `log_file` parameter to `log_files` (list of strings).
- Updated interfaces (`ColourInterface`, `FileSystemInterface`, `LoggerInterface`) to reflect new method signatures.

### Changed
- Updated `COLOUR_KEY` in `COLOURS.json` with new keys and marked old keys as deprecated for migration.
- Modified `ColourManager` to parse `FG|BG` colour values and set both foreground and background ANSI codes.
- Changed logging methods to accept `log_files` as a list, allowing simultaneous logging to multiple files.
- Updated test files to use new colour keys and multiple log file support.
- Enhanced `colour_path` to use new `!` prefixed keys for path components.

### Fixed
- Improved colour reset handling to reset both foreground and background colours.

### Notes
- Old colour keys (e.g., `ARGS`, `COMMAND`) are deprecated; migrate to new `!` prefixed keys (e.g., `!args`, `!cmd`).
- Logging methods now expect `log_files` as a list; single file can be passed as `[file_path]`.
- Ensure `COLOURS.json` is updated to use the new format for full background colour support.

## [0.4.2] - 2025-11-29

### Added
- Agent-enabled code edits: enable controlled AI agent-assisted code edits across the `Projects/tUilKit` workspace (non-binary files only). Updates are intended to be applied with review and version control.

## [0.4.1] - 2025-06-04

### Added
- `smart_diff` function to intelligently compare dataframes, ignoring row order and detecting unexpected changes via hashing.
- `find_common_columns` function to identify matching fields based on **strict column name matching** (now separated from fuzzy matching).
- `find_fuzzy_columns` function to identify similar columns based on data patterns using fuzzy matching.
- `find_composite_keys` function to determine potential multi-part key fields when no obvious single keys exist.
- `smart_merge` function with support for manual merging (`left`, `right`, `inner`, `outer`) via command-line arguments.
- JSON-based column header mapping using `tUilKit/config/COLUMN_MAPPING.json`, leveraging the existing `ConfigLoader` interface.
- JSON-based column width mapping to dynamically adjust dataframe column widths based on predefined configurations.
- `DataFrameInterface` abstract class in `tUilKit/interfaces/df_interface.py` to standardize merging and comparison operations.
- `SmartDataFrameHandler` implementation of `DataFrameInterface` to perform intelligent merging and comparisons.
- `apply_column_format` function in `formatter.py` to format dataframe columns according to known width configurations.
- **Unified test framework**: All test modules now accept a `--clean` argument for log cleanup, use consistent logging (including rainbow rows and borders), track successful/unsuccessful tests, and log exceptions in a standardized way. This framework is ready to be reused across other projects for consistent testing and reporting.

### Changed
- Improved merging logic in `smart_merge` to ensure all column mappings are applied before concatenation.
- Enhanced hashing logic in `smart_diff` to ensure row comparisons remain unaffected by column order.
- Updated `find_common_columns` to use strict column name matching; fuzzy logic is now in `find_fuzzy_columns`.
- Standardized interface methods across `df_interface.py` for easier extensibility.
- Adjusted logging configuration to support dataframe operations and new test framework.

### Fixed
- Resolved inconsistencies in dataframe merging where unknown columns disrupted the alignment.
- Fixed errors in row comparison by ensuring hashing is column-order independent.
- Addressed data formatting bugs in `apply_column_format` by properly adjusting padding rules.

### Notes
- Ensure `COLUMN_MAPPING.json` includes mappings for known data header transformations.
- Confirm `COLUMN_WIDTHS.json` is configured to handle automatic column resizing.
- All dataframe utilities are now fully integrated with `ConfigLoader` for dynamic configuration management.
- The new test framework is now the standard for all future and existing tUilKit projects.

This release significantly enhances dataframe handling capabilities and introduces a robust, reusable test framework for consistent testing and reporting across all projects. 🚀

## [0.3.1] - 2025-05-08

### Added
- `colour_path` method to `ColourManager` and `ColourInterface` for multi-colour path formatting using COLOUR_KEYs (`DRIVE`, `BASEFOLDER`, `MIDFOLDER`, `THISFOLDER`, `FILE`).
- Optional `log_to` parameter to all logging and printing functions, allowing output to terminal, file, both, or queue.
- Optional `function_log` parameter to all test functions in `test_output.py` for duplicate log file testing.
- Optional `time_stamp` parameter to logging functions for toggling timestamp display.

### Changed
- Shifted timestamp logic from `colour_log` to `log_message` in `Logger`. Now, `colour_log` passes `time_stamp=False` to `log_message` and prepends a coloured timestamp using `colour_fstr`.
- Updated `Logger` and `FileSystem` to consistently use the new `log_to` parameter.
- Updated test suite to use `logger.Colour_Mgr.colour_path(...)` for coloured path output in logs.
- Updated `colour_interface.py` to include `colour_fstr` and `colour_path` as abstract methods.
- Improved test cleanup and logging in `test_output.py` to use coloured paths and new logging features.

### Fixed
- Ensured all logging and printing functions in `Logger` accept and respect the `log_to` parameter.
- Fixed AttributeError in tests by referencing `colour_path` via `logger.Colour_Mgr.colour_path`.
- Removed redundant `time.sleep` calls from test functions, now handled in the test loop.

### Notes
- Ensure your `COLOUR_KEY` in `COLOURS.json` includes keys for `DATE`, `TIME`, `DRIVE`, `BASEFOLDER`, `MIDFOLDER`, `THISFOLDER`, and `FILE` for full colour path and timestamp support.
- All log output destinations and timestamp formatting are now fully configurable at the call site.

