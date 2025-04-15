# -*- coding: utf-8 -*-
"""
models.py: Data structures and type definitions for JSON file analysis.
"""

from typing import Dict, Union, List, Any, Literal, TypedDict, Optional

# Basic JSON types
JsonType = Union[str, int, float, bool, None, Dict[str, Any], List[Any]]
JsonValueType = Literal["string", "number", "boolean", "null", "object", "array", "unknown"]

# --- Analysis Result Structures ---

class TypeStatistics(TypedDict):
    """Counts of different JSON value types found."""
    strings: int
    numbers: int  # Includes ints and floats
    booleans: int
    nulls: int
    objects: int
    arrays: int
    total_values: int # Total non-key values encountered

class StructureSummary(TypedDict):
    """Represents the inferred structure/schema of a JSON node."""
    type: JsonValueType
    # For objects: Map of key name to the StructureSummary of its value
    keys: Optional[Dict[str, 'StructureSummary']]
    # For arrays: Summary of the types of elements found
    element_summary: Optional['StructureSummary'] # Summary if uniform, else indicates mix
    element_types: Optional[List[JsonValueType]] # List of unique types found in array
    is_empty: bool # True if object is {} or array is []

class DuplicateKeyInfo(TypedDict):
    """Information about a duplicate key found within an object."""
    path: str  # Path to the object containing the duplicate, e.g., "root.data[1].details"
    key: str   # The duplicate key name

class JsonAnalysisResult(TypedDict, total=False):
    """Top-level structure for the JSON analysis report."""
    filepath: Optional[str]
    analysis_error: Optional[str]
    file_size_bytes: Optional[int]
    root_type: Optional[JsonValueType]
    max_depth: Optional[int]
    statistics: Optional[TypeStatistics]
    structure: Optional[StructureSummary]
    duplicate_keys: Optional[List[DuplicateKeyInfo]] # List of duplicates found