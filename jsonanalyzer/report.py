# -*- coding: utf-8 -*-
"""
report.py: Generates the final JSON report from JSON analysis results.
"""

import os
import traceback
from typing import Dict, Any, Optional

from .analyzer import JsonAnalyzer
from .models import JsonAnalysisResult

def _clean_none_values_report(item: Any) -> Any:
    """
    Recursively removes keys with None values from dictionaries.
    Does NOT remove None from lists, as None is a valid JSON value.
    """
    if isinstance(item, dict):
        # Create new dict, only adding keys whose values are not None after cleaning
        cleaned_dict = {}
        for k, v in item.items():
            # Special case: Keep 'analysis_error' even if None initially, unless a real error exists.
            # However, the main generation function handles this better. Just remove None here.
            if v is not None:
                 cleaned_value = _clean_none_values_report(v)
                 cleaned_dict[k] = cleaned_value
        # Explicitly keep certain keys even if empty list/dict after cleaning, if needed
        # e.g., keep "duplicate_keys": []
        if 'duplicate_keys' in item and 'duplicate_keys' not in cleaned_dict:
            cleaned_dict['duplicate_keys'] = []
        return cleaned_dict
    elif isinstance(item, list):
        # Process items in list, but keep None values within the list
        return [_clean_none_values_report(i) for i in item]
    else:
        return item # Return non-dict/list items as is


def generate_json_report(analyzer: JsonAnalyzer) -> JsonAnalysisResult:
    """
    Generates a dictionary suitable for JSON serialization from the analyzer results,
    excluding top-level keys with None values (except potentially analysis_error).

    Args:
        analyzer: The completed JsonAnalyzer instance.

    Returns:
        A dictionary containing the structured analysis report.
    """
    # Start with the results from the analyzer
    report_data = analyzer.results.copy()

    # Ensure analysis_error from parsing/analysis takes precedence
    # (The analyzer instance already holds the consolidated error)

    # Clean None values at the top level, but keep analysis_error if it's the *only* thing present
    # A simpler approach: clean all Nones, then potentially add back a minimal error report if needed.

    try:
        # Perform any necessary final formatting or sorting here if needed
        # e.g., sort duplicate keys list by path then key
        if report_data.get("duplicate_keys"):
            report_data["duplicate_keys"] = sorted(
                report_data["duplicate_keys"],
                key=lambda d: (d.get('path', ''), d.get('key', ''))
            )

        # Clean None values recursively
        # We want to remove keys like "structure": null if analysis failed,
        # but keep "value": null within the structure summary.
        # The cleaning function should handle this.
        cleaned_report = _clean_none_values_report(report_data)

        # Ensure essential keys exist even if None was cleaned, especially for errors
        if "filepath" not in cleaned_report and report_data.get("filepath"):
             cleaned_report["filepath"] = report_data.get("filepath")
        if "analysis_error" in report_data and report_data["analysis_error"] and "analysis_error" not in cleaned_report:
             cleaned_report["analysis_error"] = report_data["analysis_error"]


        # Ensure the final type matches JsonAnalysisResult for type hinting,
        # though cleaning might make some keys optional. Cast if necessary.
        return cleaned_report # type: ignore

    except Exception as e:
         # Catch errors during the report finalization/sorting phase
         err_trace = traceback.format_exc()
         final_error = (f"Error during report generation: "
                        f"{type(e).__name__}: {e}\nTraceback:\n{err_trace}")

         # Return a minimal error report
         minimal_error_report: JsonAnalysisResult = {
             "filepath": report_data.get("filepath"),
             "analysis_error": report_data.get("analysis_error") or final_error
         }
         # Add file size if available
         if report_data.get("file_size_bytes") is not None:
             minimal_error_report["file_size_bytes"] = report_data.get("file_size_bytes")

         return minimal_error_report