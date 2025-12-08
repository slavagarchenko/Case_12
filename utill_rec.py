import os
import platform
from itertools import count
from pathlib import Path
from typing import Union, List, Tuple

PathString = Union[str, Path]


def is_windows_os() -> bool:
    return platform.system() == "Windows"


def validate_windows_path(path: PathString, depth=0) -> Tuple[bool, str]:
    problems = []
    if depth > 50:
        problems.append('Depth is too long')
        return False, problems
    path_str = str(path)
    forbidden_chars = ['*', '?', '"', '>', '<', '|']
    for char in forbidden_chars:
        if char in path_str:
            problems.append('The char is forbidden')
    if '/' in path_str:
        problems.append('Use \\ instead of /')
    if ':' in path_str:
        parts = path_str.split(':')
        if len(parts) != 2:
            problems.append('Incorrect usage of \':\'')
        if len(parts[0]) != 1 or not parts[0].isalpha():
            problems.append('Incorrect disks name \':\'' + parts[0] + '\':')
    if len(str(path)) > 260:
        problems.append('Path is too long')
    if not os.path.exists(str(path)):
        problems.append('Path does not exist')
    parent = Path(path_str).parent
    parent_str = str(parent)
    if parent_str != path_str:
        parent_valid, parent_problems = validate_windows_path(parent_str, depth + 1)
        problems.extend(parent_problems)
    is_valid = len(problems) == 0
    return is_valid, problems


def resolve_long_paths_recursive(path: PathString, prefix: str = "\\\\?\\") -> str:
    path_str = str(path)
    if path_str.startswith(prefix):
        return path_str
    if len(path_str) <= 260:
        return path_str
    long_path = prefix + os.path.abspath(path_str)
    return long_path


def collect_windows_metadata_recursive(path: PathString, max_depth: int = 10) -> Dict[str, Any]:
    def _collect_recursive(current_path, current_depth) -> Dict:
        if current_depth > max_depth:
            return None
        result = {
            'path': current_path,
            'depth': current_depth,
            'files': 0,
            'dirs': 0,
            'size': 0,
            'types': {},
            'children': []
        }
        try:
            items = os.listdir(current_path)
            for item in items:
                full_path = os.path.join(current_path, item)
                try:
                    if os.path.isfile(full_path):
                        result['files'] += 1
                        file_size = os.path.getsize(full_path)
                        result['size'] += file_size
                        _, extension = os.path.splitext(item.lower())
                        if not extension:
                            extension = 'no extension'
                        if extension not in result['types']:
                            result['types'][extension] = {
                                'count': 0,
                                'size': 0
                            }
                            result['types'][extension]['count'] += 1
                            result['types'][extension]['size'] += file_size
                    elif os.path.isdir(full_path):
                        result['dirs'] += 1
                        child_data = _collect_recursive(full_path, current_depth + 1)
                        if child_data:
                            result['children'].append(child_data)
                            result['files'] += child_data['files']
                            result['size'] += child_data['size']
                        for extension, data in child_data['types'].items():
                            if extension not in result['types']:
                                result['types'][extension] = {
                                    'count': 0,
                                    'size': 0
                                }
                                result['types'][extension]['count'] += data['count']
                                result['types'][extension]['size'] += data['size']
                except (PermissionError, OSError):
                    continue

        except Exception:
            pass

    collected = _collect_recursive(str(path), 0)
    if collected:
        return collected
    return {
        'path': str(path),
        'depth': 0,
        'files': 0,
        'dirs': 0,
        'size': 0,
        'types': {},
        'children': []
    }
       