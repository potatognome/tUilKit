
# tUilKit Project-Level Copilot Instructions

This file is minimal by design. All general rules, agent edit policies, and centralized log/config options are defined in the workspace and DEV umbrella copilot-instructions files.

Refer to:
- [Workspace copilot-instructions](../../.github/copilot-instructions.md)
- [DEV umbrella copilot-instructions](../.github/copilot-instructions.md)

Project-specific guidance:
- Use tUilKit interfaces and factory functions for all utilities.
- Document any new features or changes in the project changelog.
- All log/config paths must be config-driven (see parent instructions).

For any agent edits, follow workspace and umbrella rules unless a project-specific exception is documented here.
- All major functionality is interface-driven. See `src/tUilKit/interfaces/` for:
  - LoggerInterface
  - ColourManagerInterface
  - FileSystemInterface
  - ConfigLoaderInterface
  - DataFrameInterface
- Implementations are in `src/tUilKit/utils/`, `fs.py`, `sheets.py`, etc.
- Config files: `dict/DICT_COLOURS.py`, `dict/DICT_CODES.py`, `config/*.json`.
- Logging: supports colour, queue, multi-destination, timestamp control.
  - **LOG_FILES Dict Practice**: Create a `LOG_FILES` dict near the start of each module: `LOG_FILES = {"SESSION": "logs/RUNTIME.log", "MASTER": "logs/MASTER.log"}`. Use `logger.colour_log("!info", msg, log_files=list(LOG_FILES.values()))` for logging to all files, or `log_files=[LOG_FILES["SESSION"]]` for specific logs. This streamlines code by reducing reliance on passing log_files in function calls when log_to="both".
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
