# -*- coding: utf-8 -*-
"""
JsonAnalyzer: A JSON file structure and statistics analysis tool.

This package provides tools to analyze JSON files, extracting information about
data types, structure, depth, and potential issues like duplicate keys.
"""

# Expose key components for potential library usage
from .models import JsonAnalysisResult, StructureSummary, TypeStatistics
from .analyzer import JsonAnalyzer
from .file_handler import analyze_json_file, read_and_parse_json
from .report import generate_json_report

# Define __all__ for explicit public API if desired
__all__ = [
    "JsonAnalyzer",
    "analyze_json_file",
    "read_and_parse_json",
    "generate_json_report",
    "JsonAnalysisResult",
    "StructureSummary",
    "TypeStatistics",
]

__version__ = "1.0.0" # Example version