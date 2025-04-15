# JsonAnalysis: JSON File Structure and Statistics Analyzer

[![Build Status](https://img.shields.io/badge/build-passing-brightgreen)](https://github.com/AlexandrosLiaskos/JsonAnalysis)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

JsonAnalysis is a command-line tool and library designed to analyze the structure, data types, and basic statistics of JSON files. It parses the JSON and provides a summary report in JSON format.

This tool is useful for:

*   Quickly understanding the structure of unfamiliar JSON data.
*   Getting basic statistics about the types of values within a JSON file.
*   Identifying the maximum nesting depth.
*   Detecting duplicate keys within JSON objects (which might indicate issues).
*   Generating a schema-like overview of the JSON structure.

## Features

*   **Standard JSON Parsing:** Uses Python's built-in `json` module for parsing.
*   **Structural Analysis:**
    *   Determines the root element type (object, array, primitive).
    *   Calculates the maximum nesting depth.
    *   Generates a recursive `structure` summary showing keys (for objects) and inferred element types (for arrays).
    *   Identifies empty objects (`{}`) and arrays (`[]`).
*   **Type Statistics:** Counts the occurrences of different JSON value types (string, number, boolean, null, object, array).
*   **Duplicate Key Detection:** Reports the paths and keys where duplicates are found within objects.
*   **File Information:** Includes the filepath and file size in the report.
*   **JSON Output:** Provides results in a structured JSON format.
*   **CLI Interface:** Easy-to-use command-line tool.
*   **Output Options:**
    *   Print JSON to standard output.
    *   Write JSON to a specified file.
    *   Control JSON formatting (pretty-printed or compact).
    *   Optionally copy the JSON output to the clipboard (requires `pyperclip`).
*   **Error Handling:** Gracefully handles file not found errors, permission errors, and JSON decoding errors, reporting them within the JSON output.
*   **Library Usage:** Core components can be imported and used programmatically.

## Installation

1.  **Clone the repository (or create the files locally):**
    ```bash
    # If cloning:
    # git clone https://github.com/AlexandrosLiaskos/JsonAnalysis.git 
    # cd JsonAnalysis
    ```

2.  **Install the package:**
    Using pip, you can install the package locally. This makes the `jsonanalyzer` command and `python -m jsonanalyzer` available.
    ```bash
    pip install .
    ```
    *   Alternatively, for development: `pip install -e .`

3.  **Optional Dependencies:**
    To use the `--copy` feature, you need to install `pyperclip`:
    ```bash
    pip install pyperclip
    ```

## Usage

### Command-Line Interface (CLI)

The primary way to use JsonAnalysis is via the command line.

```bash
jsonanalyzer <filepath> [options]
# OR
python -m jsonanalyzer <filepath> [options]
```

**Arguments:**

*   `filepath`: Path to the JSON file to analyze.

**Options:**

*   `-o FILE`, `--output FILE`: Path to write the JSON output file. If omitted, prints to stdout.
*   `--copy`: Copy the generated JSON report to the clipboard (requires `pyperclip`).
*   `--pretty` / `--no-pretty`: Output formatted (pretty-printed) JSON (default) or compact JSON (`--no-pretty`).

**Examples:**

```bash
# Analyze a file and print pretty JSON to stdout
jsonanalyzer data.json

# Analyze a file and save compact JSON to report.json
python -m jsonanalyzer config.json -o report.json --no-pretty

# Analyze a file, print pretty JSON to stdout, and copy it to the clipboard
jsonanalyzer results.json --copy
```

### Library Usage

You can also use JsonAnalysis programmatically.

```python
import json
import sys
from jsonanalyzer import analyze_json_file, generate_json_report

filepath = "path/to/your_data.json"

try:
    # 1. Analyze the file (reads, parses, analyzes)
    analyzer_instance = analyze_json_file(filepath)

    # 2. Generate the report dictionary
    report_data = generate_json_report(analyzer_instance)

    # 3. Process the report
    if report_data.get("analysis_error"):
        print(f"Analysis Error: {report_data['analysis_error']}", file=sys.stderr)
        # Handle error appropriately

    json_output = json.dumps(report_data, indent=2, ensure_ascii=False)
    print(json_output)

except Exception as e:
    print(f"An unexpected error occurred: {e}", file=sys.stderr)

```

## Output Format

The tool outputs a JSON object containing the analysis results. Top-level keys with `None` values are generally removed, except for `analysis_error` if an error occurred.

**Top-Level Keys:**

*   `filepath`: Absolute path to the analyzed file.
*   `analysis_error`: String containing an error message if file/parsing/analysis errors occurred. Omitted if no error.
*   `file_size_bytes`: Size of the JSON file in bytes.
*   `root_type`: Type of the top-level JSON element ("object", "array", "string", etc.).
*   `max_depth`: Maximum nesting level found in the JSON structure (root is depth 0).
*   `statistics`: An object containing counts of different value types (`strings`, `numbers`, `booleans`, `nulls`, `objects`, `arrays`, `total_values`).
*   `structure`: A nested object representing the inferred schema/structure. See Structure Summary below.
*   `duplicate_keys`: A list of objects, each detailing a duplicate key found within an object (`path`, `key`). Sorted by path then key.

**Structure Summary (`structure` key):**

This provides a recursive overview:

```json
{
  "type": "object | array | string | number | boolean | null",
  "is_empty": true | false, // Indicates if object is {} or array is []
  // Only for "object" type:
  "keys": {
    "key_name1": { /* Recursive StructureSummary for value of key1 */ },
    "key_name2": { /* ... */ }
    // ...
  },
  // Only for "array" type:
  "element_types": ["string", "number", ...], // List of unique value types found in the array
  "element_summary": { /* StructureSummary if elements are uniform, null otherwise or if mixed/complex */ }
}
```
*   For arrays with *uniform* structure (e.g., all strings, or all objects with the exact same keys and value types), `element_summary` will show the structure of one element.
*   For arrays with *mixed* types or non-uniform structures, `element_summary` might be simpler (e.g., just showing the type if all elements share one basic type but differ internally) or `null`. `element_types` always lists all unique base types found.

**Example JSON Output (Snippet):**

```json
{
  "filepath": "/path/to/example.json",
  "file_size_bytes": 512,
  "root_type": "object",
  "max_depth": 3,
  "duplicate_keys": [
      { "path": "root.items[1]", "key": "id" }
  ],
  "statistics": {
    "strings": 15,
    "numbers": 5,
    "booleans": 2,
    "nulls": 1,
    "objects": 4,
    "arrays": 1,
    "total_values": 28
  },
  "structure": {
    "type": "object",
    "is_empty": false,
    "keys": {
      "metadata": {
        "type": "object",
        "is_empty": false,
        "keys": {
          "timestamp": { "type": "string", "is_empty": false },
          "source": { "type": "string", "is_empty": false }
        }
      },
      "items": {
        "type": "array",
        "is_empty": false,
        "element_types": ["object"],
        "element_summary": { // Assuming items are objects with similar structure
          "type": "object",
          "is_empty": false,
          "keys": {
            "id": { "type": "number", "is_empty": false },
            "name": { "type": "string", "is_empty": false },
            "active": { "type": "boolean", "is_empty": false },
            "description": { "type": "null", "is_empty": false }
          }
        }
      },
      "config": {
         "type": "object",
         "is_empty": true,
         "keys": {}
      }
    }
  }
}
```

## Contributing

Contributions are welcome! Please follow standard GitHub fork & pull request workflows. Open an issue to discuss significant changes first.

## License

This project is licensed under the MIT License.
