# Project Name
tUilKit
**Current version: 0.5.1**

tUilKit (formerly utilsbase) is a modular Python toolkit providing utility functions, dictionaries, and configuration for development projects.  
The package is structured around clear **interfaces** for logging, colour management, file system operations, and configuration loading, making it easy to extend or swap implementations.  
tUilKit is organized into three main components:
- **/config**: JSON files for customization and configuration
- **/dict**: Python dictionaries and constants (e.g., ANSI codes, RGB values)
- **/utils**: Toolkit modules implementing the interfaces

## Folder Structure 


```
/src
        /config
            BORDER_PATTERNS.json        # Border Patterns
            COLUMN_MAPPING.json         # DataFrame column mapping
            COLOURS.json                # Foreground text COLOUR_KEY and RGB Reference
            GLOBAL_CONFIG.json          # Folder paths and logging/display options
            config.py                   # ConfigLoader implementation
        /dict
            DICT_CODES.py               # ANSI escape code parts for sequencing
            DICT_COLOURS.py             # RGB ANSI escape codes for sequencing
        /interfaces
            colour_interface.py         # ColourInterface (abstract base class)
            config_loader_interface.py  # ConfigLoaderInterface (abstract base class)
            df_interface.py             # DataFrameInterface (abstract base class)
            file_system_interface.py    # FileSystemInterface (abstract base class)
            logger_interface.py         # LoggerInterface (abstract base class)
        /utils
            fs.py                       # Core - File system operations (FileSystem)
            output.py                   # Core - Printing/Debugging/Logging (Logger, ColourManager)
            sheets.py                   # Primary - CSV/XLSX utilities
            formatter.py                # Primary Extension - formatting utilities (early development)
            pdf.py                      # Add-on - PDF file utilities (early development)
            sql.py                      # Add-on - SQL query utilities (planned)
            calc.py                     # Add-on - Specialized calculations
            wallet.py                   # Add-on - Specialized crypto wallet utilities
            data.py                     # Add-on - Specialized data utilities
    /tests
        /testLogs
        test_module.py                  # Tests for interfaces and project folder logic
        test_output.py                  # Tests for output/logging functions
```

## Interfaces

tUilKit uses Python abstract base classes to define clear interfaces for:
- **LoggerInterface**: Logging, coloured output, and border printing
- **ColourInterface**: Colour formatting and ANSI code management
- **FileSystemInterface**: File and folder operations
- **ConfigLoaderInterface**: Configuration loading and path resolution
- **DataFrameInterface**: Data frame operations

All implementations in `/utils` and `/config` inherit from these interfaces, ensuring modularity and testability.

## Installation
Follow these instructions to install and set up the project:

```bash
# Navigate to the project directory
cd tUilKit

# (Optional) Create and activate a virtual environment
# python -m venv venv
# source venv/bin/activate  # On Windows use `venv\Scripts\activate`

# Install dependencies
pip install -r requirements.txt
```

## Usage

Sample usage and tests can be found in the `/tests` folder.

```python
# Example: Using Logger and ColourManager

from tUilKit.utils.output import Logger, ColourManager
import json, os

# Load colour config
COLOUR_CONFIG_PATH = os.path.join("src", "tUilKit", "config", "COLOURS.json")
with open(COLOUR_CONFIG_PATH, "r") as f:
    colour_config = json.load(f)

colour_manager = ColourManager(colour_config)
logger = Logger(colour_manager)

log_file = "example.log"
logger.colour_log("INFO", "This is a coloured log message.", log_file=log_file)
logger.log_done(log_file=log_file)
```

## Contributing
If you would like to contribute, please fork the repository and use a feature branch. Pull requests are warmly welcome.

We’re actively seeking contributors to help enhance tUilKit! Whether you’re passionate about terminal functionality, advanced data operations, or document creation, there’s plenty of room to leave your mark.

### Areas for Contribution

- **Enhanced ANSI Sequences**:  
    - Fetching user keystrokes, moving cursor, background colours, advanced terminal features.
- **DataFrame / Spreadsheet Functionality**:  
    - Smart diff, smart merging, custom autoformatting and updates to the DataFrameInterface and sheets utilities.
- **LaTeX and PDF Functionality**:  
    - Reading/writing LaTeX, PDF file manipulation (generation, formatting, searching, editing).

## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements
- Thanks to everyone who contributed to this project.