import os
import platform
from pathlib import Path
from typing import Union, List, Tuple, Dict, Any
from functools import lru_cache

PathString = Union[str, Path]


def validate_windows_path_recursive(path: PathString, depth: int = 0) -> Tuple[bool, List[str]]:
    """
    Recursively validate Windows path and all its parent directories.

    Args:
        path: Path to validate
        depth: Current recursion depth (for internal use)

    Returns:
        Tuple containing:
        - True if entire path is valid, False otherwise
        - List of problematic path segments with error messages
    """
    MAX_RECURSION_DEPTH = 50
    problems = []

    if depth > MAX_RECURSION_DEPTH:
        problems.append(
            f'Maximum recursion depth exceeded ({MAX_RECURSION_DEPTH})')
        return False, problems

    path_str = str(path)

    forbidden_chars = ['*', '?', '"', '>', '<', '|']

    for char in forbidden_chars:
        if char in path_str:
            problems.append(
                f'Forbidden character "{char}" in path segment: {path_str}')

    if '/' in path_str and '\\' not in path_str.replace('://', ''):
        problems.append(f'Use \\\\ instead of / in path: {path_str}')

    if ':' in path_str:
        parts = path_str.split(':')

        if len(parts) != 2:
            problems.append(f'Incorrect usage of ":" in path: {path_str}')

        elif len(parts[0]) != 1 or not parts[0].isalpha():
            problems.append(
                f'Invalid drive letter "{parts[0]}" in path: {path_str}')

    if len(path_str) > 260 and not path_str.startswith('\\\\?\\'):
        problems.append(f'Path exceeds 260 characters: {len(path_str)} chars')

    if depth == 0 and not os.path.exists(path_str):
        problems.append(f'Path does not exist: {path_str}')

    parent = Path(path_str).parent
    parent_str = str(parent)

    if parent_str != path_str and parent_str not in ['', '.', '/', '\\']:

        if not (path_str.startswith('\\\\') and path_str.count('\\') <= 3):
            parent_valid, parent_problems = validate_windows_path_recursive(
                parent_str, depth + 1)
            problems.extend(parent_problems)

    is_valid = len(problems) == 0
    return is_valid, problems


@lru_cache(maxsize=128)
def resolve_long_paths_recursive(path: PathString, prefix: str = "\\\\?\\") -> str:
    """
    Recursively convert long Windows paths with UNC support.

    Args:
        path: Path to convert
        prefix: Prefix for long paths (default: "\\\\?\\")

    Returns:
        Converted path with prefix if needed
    """
    path_str = str(path)

    if path_str.startswith(prefix):
        return path_str

    if path_str.startswith('\\\\'):

        if len(path_str) > 260 and not path_str.startswith('\\\\?\\UNC\\'):
            return '\\\\?\\UNC\\' + path_str[2:]
        return path_str

    if len(os.path.abspath(path_str)) > 260:

        if not path_str.startswith(prefix):
            abs_path = os.path.abspath(path_str)
            return prefix + abs_path

    return os.path.normpath(path_str)


def collect_windows_metadata_recursive(path: PathString, max_depth: int = 10) -> Dict[str, Any]:
    """
    Recursively collect file system metadata for Windows.

    Args:
        path: Starting path for metadata collection
        max_depth: Maximum recursion depth

    Returns:
        Nested dictionary with metadata structure
    """
    def _collect_recursive(current_path: str, current_depth: int, visited: set) -> Dict[str, Any]:
        """Internal recursive collection function"""
        if current_depth > max_depth or current_path in visited:
            return None

        visited.add(current_path)
        result = {
            'path': current_path,
            'depth': current_depth,
            'files': 0,
            'dirs': 0,
            'size': 0,
            'types': {},
            'attributes': {'hidden': 0, 'system': 0, 'readonly': 0},
            'children': []
        }

        try:
            items = os.listdir(current_path)

            for item in items:
                full_path = os.path.join(current_path, item)

                try:
                    if os.path.islink(full_path):
                        continue

                    if os.path.isfile(full_path):
                        result['files'] += 1

                        try:
                            file_size = os.path.getsize(full_path)
                            result['size'] += file_size

                            _, extension = os.path.splitext(item)
                            extension = extension.lower() if extension else 'no_extension'

                            if extension not in result['types']:
                                result['types'][extension] = {
                                    'count': 0,
                                    'size': 0
                                }

                            result['types'][extension]['count'] += 1
                            result['types'][extension]['size'] += file_size

                            try:
                                attrs = os.stat(full_path).st_file_attributes

                                if attrs & 0x02:
                                    result['attributes']['hidden'] += 1

                                if attrs & 0x04:
                                    result['attributes']['system'] += 1

                                if attrs & 0x01:
                                    result['attributes']['readonly'] += 1

                            except (AttributeError, OSError):
                                pass

                        except (OSError, PermissionError):
                            continue

                    elif os.path.isdir(full_path):
                        result['dirs'] += 1

                        if current_depth < max_depth:
                            child_data = _collect_recursive(
                                full_path, current_depth + 1, visited)
                            if child_data:
                                result['children'].append(child_data)

                                result['files'] += child_data['files']
                                result['dirs'] += child_data['dirs']
                                result['size'] += child_data['size']

                                for ext, data in child_data['types'].items():
                                    if ext not in result['types']:
                                        result['types'][ext] = {
                                            'count': 0, 'size': 0}
                                    result['types'][ext]['count'] += data['count']
                                    result['types'][ext]['size'] += data['size']

                                for attr in ['hidden', 'system', 'readonly']:
                                    result['attributes'][attr] += child_data['attributes'][attr]

                except (PermissionError, OSError):
                    continue

        except (PermissionError, OSError, FileNotFoundError):
            pass

        return result

    visited = set()
    collected_data = _collect_recursive(str(path), 0, visited)

    if collected_data is None:
        return {
            'path': str(path),
            'depth': 0,
            'files': 0,
            'dirs': 0,
            'size': 0,
            'types': {},
            'attributes': {'hidden': 0, 'system': 0, 'readonly': 0},
            'children': []
        }

    return collected_data
