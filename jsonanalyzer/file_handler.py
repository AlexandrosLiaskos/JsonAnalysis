# -*- coding: utf-8 -*-
"""
file_handler.py: Handles reading and parsing JSON files.
"""

import json
import os
import traceback
from typing import Tuple, Optional

from .analyzer import JsonAnalyzer # Import analyzer to store initial errors
from .models import JsonType

def read_and_parse_json(filepath: str) -> Tuple[Optional[JsonType], Optional[str], Optional[int]]:
    """
    Reads and parses a JSON file.

    Handles file existence checks and catches parsing errors.

    Args:
        filepath: The path to the JSON file.

    Returns:
        A tuple containing:
        - The parsed JSON data (Python object) or None if an error occurred.
        - An error message string if an error occurred, otherwise None.
        - The file size in bytes, or None if the file couldn't be accessed.
    """
    error_message: Optional[str] = None
    parsed_data: Optional[JsonType] = None
    file_size: Optional[int] = None

    if not os.path.exists(filepath):
        error_message = f"Error: File not found at '{filepath}'"
        return None, error_message, None
    if not os.path.isfile(filepath):
         error_message = f"Error: Input path '{filepath}' is a directory, not a file."
         return None, error_message, None
    # Optional: Check extension, though not strictly necessary for JSON
    # if not filepath.lower().endswith(".json"):
    #     print(f"Warning: File '{filepath}' does not have a .json extension.", file=sys.stderr)

    try:
        file_size = os.path.getsize(filepath)
        with open(filepath, 'r', encoding='utf-8') as f:
            parsed_data = json.load(f)
    except FileNotFoundError: # Should be caught above, but belt-and-suspenders
        error_message = f"Error: File not found at '{filepath}'"
        file_size = None # Reset size if open failed after initial check
    except PermissionError:
         error_message = f"Error: Permission denied reading file '{filepath}'"
         file_size = None
    except json.JSONDecodeError as e:
        error_message = (
            f"JSON Decode Error: Invalid JSON syntax in '{filepath}' near line {e.lineno} column {e.colno}:\n"
            f"  Detail: {e.msg}"
        )
        parsed_data = None # Ensure data is None on decode error
    except Exception as e:
        # Catch other potential errors during file reading or parsing
        err_trace = traceback.format_exc()
        error_message = (f"Unexpected Error: Failed reading or parsing '{filepath}'.\n"
                         f"  Error: {type(e).__name__}: {e}\nTraceback:\n{err_trace}")
        parsed_data = None
        # Keep file_size if it was obtained before the error

    return parsed_data, error_message, file_size

def analyze_json_file(filepath: str) -> JsonAnalyzer:
    """
    Reads, parses, and analyzes a JSON file using JsonAnalyzer.

    Args:
        filepath: The path to the JSON file.

    Returns:
        A JsonAnalyzer instance containing the analysis results or error information.
    """
    analyzer = JsonAnalyzer()
    analyzer.results["filepath"] = os.path.abspath(filepath) if filepath else None

    parsed_data, error_message, file_size = read_and_parse_json(filepath)

    analyzer.results["file_size_bytes"] = file_size

    if error_message:
        analyzer.results["analysis_error"] = error_message
        # Ensure other fields reflect the failure state
        analyzer.results["root_type"] = None
        analyzer.results["max_depth"] = None
        analyzer.results["statistics"] = None
        analyzer.results["structure"] = None
        analyzer.results["duplicate_keys"] = []
    elif parsed_data is not None:
        # Only proceed with analysis if parsing was successful
        analyzer.analyze(parsed_data)
    else:
        # This case should theoretically be covered by error_message, but as a fallback:
        analyzer.results["analysis_error"] = f"Unknown error: Failed to parse '{filepath}' but no specific error message was generated."

    return analyzer