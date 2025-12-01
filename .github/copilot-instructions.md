<!-- tUilKit project-level copilot instructions (merged & expanded) -->
# tUilKit — Project Guidance for Automated Agents

Purpose
- tUilKit is a utility development toolkit to improve common CLI app functions and shorten development cycles by improving runtime output readability, configuration handling, filesystem utilities, logging, dataframe utilities, and a standardized testing framework.

Primary Focus Areas
- Colour management and terminal-friendly formatting.
- File system helpers and safe IO utilities.
- JSON-driven configuration loading and validation.
- DataFrame utilities for smart merging/diffing and schema-aware operations.
- Centralized logging and log parsing, with deterministic log formats for testing.
- A small, consistent test harness and expected-output logs for regression testing.

Important Interfaces (authoritative source: `src/tUilKit/interfaces/`)
- `LoggerInterface` — multi-destination logging, timestamp control, and color-aware formatting.
- `ColourManagerInterface` — `colour_fstr`, `colour_path`, and canonical colour keys.
- `FileSystemInterface` — cross-platform path helpers and atomic file operations.
- `ConfigLoaderInterface` — loading, validating, and merging JSON configs.
- `DataFrameInterface` — standardized merge/diff API with support for `config_loader=None` and hashing-based row comparisons.

File Layout (key folders)
- `src/tUilKit/config/` — JSON configuration files (e.g., `COLOURS.json`, `COLUMN_MAPPING.json`).
- `src/tUilKit/dict/` — code-backed dictionaries and mappings.
- `src/tUilKit/interfaces/` — interface definitions; changes here are breaking and require tests/implementations updates.
- `src/tUilKit/utils/` — concrete implementations and helpers.
- `tests/` — unit and integration tests.
  - `tests/testInputFiles/` — input assets used in tests.
  - `tests/testOutputFiles/` — expected data outputs.
  - `tests/testOutputLogs/` — expected log outputs used to validate log formatting and behaviour.

Agent Rules & Best Practices
- Add features via interfaces: prefer adding methods to interfaces and implementing them in `utils/`.
- Backwards compatibility: JSON config changes must provide sensible defaults and migration notes.
- Tests: every behavioral change must include tests. Update `tests/testOutputLogs/` only when changing log format intentionally and include test updates that assert the new format.
- Dependencies: add runtime dependencies sparingly. Update `pyproject.toml` and `setup.py` when necessary.
- Documentation: update `README.md` and `CHANGELOG.md` (agents may prepare draft entries marked `DRAFT` for human review).

When to Modify Which Files
- Modify `src/tUilKit/utils/` and `tests/` freely for bug fixes, small refactors, and new features.
- Modify `src/tUilKit/interfaces/` only when needed — adding interface methods requires updating implementations and tests.
- Modify JSON files in `src/tUilKit/config/` for configuration improvements; include examples and update documentation.
- Avoid editing historical log archives except as part of a controlled test update.
 - Avoid editing historical log archives except as part of a controlled test update.
 - Avoid modifying OS metadata files (for example `desktop.ini`) and other hidden system files; these should remain untouched by agents.

Testing & Local Development (PowerShell)
```powershell
cd Projects\tUilKit
python -m venv .venv
.\.venv\Scripts\Activate
pip install -r requirements.txt   # if present
pip install -e .                  # editable install
pytest -q
```

Commit & Branching Guidelines
- Branch naming: `agent/<short-description>` for agent work.
- Commit message format:
  - `tUilKit: <short summary>`
  - Body: `Why: <reason>\nTests: <added/updated/passed>`
- Changelog: prepare `DRAFT` entries; human maintainer will finalize.

Porting / Retrofitting Guidance
- Use `Projects/_PORTS/` as staging for porting external repositories to use `tUilKit`.
- Steps: copy repo → update imports to `tUilKit` → create adapters implementing interfaces → add tests → run test suite.

Contact & Review
- All agent edits require human review before merging. Notify: Daniel Austin <the.potato.gnome@gmail.com>.

This file merges the prior project-level guidance with the expanded guidance file. A backup was created as `.bak3` prior to this change.
# Copilot Instructions for tUilKit

## Project Overview
- Modular Python toolkit for data, file, config, and logging utilities.
- Python 3.7+; main code in `src/tUilKit/`.
- Key dependencies: pandas, fuzzywuzzy (no python-Levenshtein).

## Architecture & Conventions
- All major functionality is interface-driven. See `src/tUilKit/interfaces/` for:
  - LoggerInterface
  - ColourManagerInterface
  - FileSystemInterface
  - ConfigLoaderInterface
  - DataFrameInterface
- Implementations are in `src/tUilKit/utils/`, `fs.py`, `sheets.py`, etc.
- Config files: `dict/DICT_COLOURS.py`, `dict/DICT_CODES.py`, `config/*.json`.
- Logging: supports colour, queue, multi-destination, timestamp control.
- Test framework: standardized, robust, per-test logs, rainbow/border output, `--clean` arg for log cleanup.

## Coding Guidelines for AI Agents
- Always use interface methods for core functionality.
- When adding new features, update both interface and implementation.
- For DataFrameInterface.merge, ensure signature includes `config_loader=None` for consistency.
- Use config files via ConfigLoader for all customizations.
- Logging should be modular, support colour, and allow multiple destinations.
- Tests should follow the standardized loop: initialize config, run tests, log per-test and global results, handle exceptions, support `--clean`.
- Do not use python-Levenshtein; use fuzzywuzzy only.
- Packaging: update `requirements.txt`, `pyproject.toml`, and `setup.py` for new dependencies.
- Document all major changes in `CHANGELOG.md` and `README.md`.

## File Locations
- Interfaces: `src/tUilKit/interfaces/`
- Implementations: `src/tUilKit/utils/`, `fs.py`, `sheets.py`
- Configs: `dict/`, `config/`
- Tests: `tests/`
- Docs: `README.md`, `CHANGELOG.md`

## Best Practices
- Keep code modular and interface-driven.
- Prefer config-driven customization.
- Ensure all tests pass before publishing.
- Maintain clear, concise documentation.

---

If any section is unclear or incomplete, please ask for clarification or request updates.
