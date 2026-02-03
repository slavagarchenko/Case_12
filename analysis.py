import os
from typing import Dict, Any, Tuple
from collections import defaultdict
import utils
import navigation


def count_files(path: str) -> Tuple[bool, int]:
    """
    Recursively counts all files in the specified directory 
        and its subdirectories.

    Args:
        path: The directory path to scan.

    Returns:
        A tuple containing:
        - success flag (True if scan completed successfully)
        - total number of files (excluding symbolic links)
    """
    valid, items = navigation.list_directory(path)

    if not valid:
        return False, 0

    total = 0

    for item in items:
        full_path = os.path.join(path, item['name'])

        if os.path.islink(full_path):
            continue

        if item['type'] == 'file':
            total += 1

        elif item['type'] == 'dir':
            ok, count = count_files(full_path)
            if ok:
                total += count

    return True, total


def count_bytes(path: str) -> Tuple[bool, int]:
    """
    Recursively calculates the total size of all files 
        in the specified directory.

    Args:
        path: The directory path to scan.

    Returns:
        A tuple containing:
        - success flag (True if scan completed successfully)
        - total size in bytes (excluding symbolic links)
    """
    valid, items = navigation.list_directory(path)

    if not valid:
        return False, 0

    total_size = 0

    for item in items:
        full_path = os.path.join(path, item['name'])

        if os.path.islink(full_path):
            continue

        if item['type'] == 'file':
            total_size += item['size']

        elif item['type'] == 'dir':
            ok, size = count_bytes(full_path)
            if ok:
                total_size += size

    return True, total_size


def analyze_windows_file_types(path: str) \
        -> Tuple[bool, Dict[str, Dict[str, Any]]]:
    """
    Analyzes file types by extension in the specified directory 
    and its subdirectories.

    Args:
        path: The directory path to scan.

    Returns:
        A tuple containing:
        - success flag (True if scan completed successfully)
        - dictionary mapping file extensions to statistics including:
            - 'count': number of files with that extension
            - 'bytes': total size of files with that extension
    """
    valid, items = navigation.list_directory(path)

    if not valid:
        return False, {}

    stats = defaultdict(lambda: {'count': 0, 'bytes': 0})

    for item in items:
        full_path = os.path.join(path, item['name'])

        if os.path.islink(full_path):
            continue

        if item['type'] == 'file':
            _, ext = os.path.splitext(item['name'])
            ext = ext.lower()

            stats[ext]['count'] += 1
            stats[ext]['bytes'] += item['size']

        elif item['type'] == 'dir':
            ok, sub = analyze_windows_file_types(full_path)

            if ok:
                for ext, data in sub.items():
                    stats[ext]['count'] += data['count']
                    stats[ext]['bytes'] += data['bytes']

    return True, dict(stats)


def get_windows_file_attributes_stats(path: str) -> Dict[str, int]:
    """
    Collects Windows file attribute statistics 
       for the specified directory.

    Args:
        path: The directory path to scan.

    Returns:
        A dictionary containing counts for:
        - 'hidden': number of hidden files
        - 'system': number of system files
        - 'readonly': number of read-only files
    """
    valid, items = navigation.list_directory(path)

    if not valid:
        return {'hidden': 0, 'system': 0, 'readonly': 0}

    stats = {'hidden': 0, 'system': 0, 'readonly': 0}

    FILE_ATTRIBUTE_READONLY = 0x1
    FILE_ATTRIBUTE_SYSTEM = 0x4

    for item in items:
        full_path = os.path.join(path, item['name'])

        if os.path.islink(full_path):
            continue

        try:
            attrs = os.stat(full_path).st_file_attributes

            if item['type'] == 'file':
                if utils.is_hidden_windows_file(full_path):
                    stats['hidden'] += 1

                if attrs & FILE_ATTRIBUTE_SYSTEM:
                    stats['system'] += 1

                if attrs & FILE_ATTRIBUTE_READONLY:
                    stats['readonly'] += 1

            elif item['type'] == 'dir':
                sub = get_windows_file_attributes_stats(full_path)
                stats['hidden'] += sub['hidden']
                stats['system'] += sub['system']
                stats['readonly'] += sub['readonly']

        except (OSError, PermissionError):
            continue

    return stats


def show_windows_directory_stats(path: str) -> bool:
    """
    Displays comprehensive directory statistics including file counts, 
        sizes, file types, and Windows file attributes.

    Args:
        path: The directory path to analyze.

    Returns:
        True if analysis completed successfully, False otherwise.
    """
    print('\n===== DIRECTORY ANALYSIS =====')
    print(f'Path: {path}')

    ok_files, file_count = count_files(path)

    if not ok_files:
        print('Error: Cannot scan directory.')
        return False

    print(f'\nTotal files: {file_count}')

    ok_size, total_size = count_bytes(path)

    if ok_size:
        print(f'Total size: {utils.format_size(total_size)}')

    else:
        print('Size scan error.')

    ok_types, types = analyze_windows_file_types(path)

    if ok_types:
        print('\nFile types:')

        for ext, info in sorted(types.items(), key=lambda x: -x[1]['count']):
            print(
                f"{ext or '[no extension]'}: {info['count']} files, "
                f"{utils.format_size(info['bytes'])}")

    attrs = get_windows_file_attributes_stats(path)

    print('\nAttributes:')
    print(f"  Hidden:   {attrs['hidden']}")
    print(f"  System:   {attrs['system']}")
    print(f"  Readonly: {attrs['readonly']}")

    print('\n===== END =====\n')
    return True
