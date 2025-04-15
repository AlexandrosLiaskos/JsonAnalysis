# -*- coding: utf-8 -*-
"""
analyzer.py: Core logic for analyzing JSON data structure.
"""

import json
from typing import Any, Tuple, List, Dict, Set
from collections import Counter

from .models import (
    JsonType, JsonValueType, TypeStatistics, StructureSummary,
    DuplicateKeyInfo, JsonAnalysisResult
)

def _get_value_type(value: JsonType) -> JsonValueType:
    """Determines the JSON type string for a given Python value."""
    if isinstance(value, str):
        return "string"
    elif isinstance(value, bool):
        return "boolean"
    elif isinstance(value, (int, float)):
        return "number"
    elif isinstance(value, dict):
        return "object"
    elif isinstance(value, list):
        return "array"
    elif value is None:
        return "null"
    else:
        return "unknown" # Should ideally not happen with standard JSON

def _analyze_recursive(
    node: JsonType,
    current_path: str,
    current_depth: int,
    stats: TypeStatistics,
    duplicates: List[DuplicateKeyInfo],
    max_depth_tracker: List[int]
) -> StructureSummary:
    """
    Recursively analyzes a JSON node (value, object, or array).

    Args:
        node: The current JSON node to analyze.
        current_path: The path string to this node (e.g., "root.key[0]").
        current_depth: The nesting depth of this node.
        stats: Mutable dictionary to accumulate type counts.
        duplicates: Mutable list to accumulate duplicate key info.
        max_depth_tracker: Mutable list containing one element (max depth found so far).

    Returns:
        A StructureSummary dictionary describing the node.
    """
    node_type = _get_value_type(node)
    stats['total_values'] += 1 # Count every value node
    max_depth_tracker[0] = max(max_depth_tracker[0], current_depth)

    summary: StructureSummary = {
        "type": node_type,
        "keys": None,
        "element_summary": None,
        "element_types": None,
        "is_empty": False,
    }

    if node_type == "object":
        stats['objects'] += 1
        obj_node = node # Type assertion hint
        summary["is_empty"] = not bool(obj_node)
        summary["keys"] = {}
        seen_keys: Set[str] = set()

        for key, value in obj_node.items():
            # Check for duplicate keys within this specific object
            if key in seen_keys:
                duplicates.append({"path": current_path, "key": key})
            else:
                seen_keys.add(key)

            child_path = f"{current_path}.{key}" if current_path else key
            summary["keys"][key] = _analyze_recursive(
                value, child_path, current_depth + 1, stats, duplicates, max_depth_tracker
            )

    elif node_type == "array":
        stats['arrays'] += 1
        arr_node = node # Type assertion hint
        summary["is_empty"] = not bool(arr_node)
        element_summaries: List[StructureSummary] = []
        element_types: List[JsonValueType] = []

        for i, item in enumerate(arr_node):
            child_path = f"{current_path}[{i}]"
            item_summary = _analyze_recursive(
                item, child_path, current_depth + 1, stats, duplicates, max_depth_tracker
            )
            element_summaries.append(item_summary)
            element_types.append(item_summary["type"])

        unique_types = sorted(list(set(element_types)))
        summary["element_types"] = unique_types

        # Try to create a representative summary for array elements
        if not element_summaries:
             summary["element_summary"] = None # Empty array
        elif len(unique_types) == 1:
             # If all elements have the same basic type and structure, use the first one as representative
             # A more sophisticated approach could merge structures, but this is simpler
             first_summary = element_summaries[0]
             is_uniform = all(s == first_summary for s in element_summaries) # Simple structural check
             if is_uniform:
                 summary["element_summary"] = first_summary
             else:
                 # Same basic type but different structures (e.g., array of objects with different keys)
                 summary["element_summary"] = {"type": unique_types[0], "keys": None, "element_summary": None, "element_types": None, "is_empty": False} # Indicate type but not structure
        else:
             # Mixed types
             summary["element_summary"] = None # Cannot provide single summary for mixed types

    elif node_type == "string":
        stats['strings'] += 1
    elif node_type == "number":
        stats['numbers'] += 1
    elif node_type == "boolean":
        stats['booleans'] += 1
    elif node_type == "null":
        stats['nulls'] += 1
    # 'unknown' type is just counted in total_values

    return summary


class JsonAnalyzer:
    """
    Analyzes parsed JSON data to extract structural information and statistics.
    """
    def __init__(self) -> None:
        self.results: JsonAnalysisResult = {
            "filepath": None,
            "analysis_error": None,
            "file_size_bytes": None,
            "root_type": None,
            "max_depth": 0,
            "statistics": None,
            "structure": None,
            "duplicate_keys": [],
        }
        self.parsed_data: Optional[JsonType] = None

    def analyze(self, parsed_data: JsonType) -> None:
        """
        Performs the analysis on the already parsed JSON data.

        Args:
            parsed_data: The Python object resulting from json.load() or json.loads().
        """
        self.parsed_data = parsed_data
        self.results['root_type'] = _get_value_type(parsed_data)

        # Initialize statistics counters
        stats: TypeStatistics = {
            "strings": 0, "numbers": 0, "booleans": 0, "nulls": 0,
            "objects": 0, "arrays": 0, "total_values": 0
        }
        duplicates: List[DuplicateKeyInfo] = []
        max_depth_tracker = [0] # Use list to pass by reference

        try:
            # Start recursive analysis from the root
            self.results["structure"] = _analyze_recursive(
                parsed_data, "root", 0, stats, duplicates, max_depth_tracker
            )
            self.results["statistics"] = stats
            self.results["max_depth"] = max_depth_tracker[0]
            self.results["duplicate_keys"] = duplicates

        except Exception as e:
            import traceback
            err_trace = traceback.format_exc()
            self.results["analysis_error"] = (
                f"Unexpected Analysis Error: Failed processing JSON data.\n"
                f"  Error: {type(e).__name__}: {e}\nTraceback:\n{err_trace}"
            )
            # Reset potentially partial results if analysis failed mid-way
            self.results["structure"] = None
            self.results["statistics"] = None
            self.results["max_depth"] = None
            self.results["duplicate_keys"] = []