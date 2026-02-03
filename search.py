import os
import re
from typing import List, Dict, Any, Tuple
import utils
import navigation
import analysis
import ru_local


def find_files_windows(pattern: str, path: str, case_sensitive: bool = False) -> List[str]:
    """
    Search files by pattern in Windows file system.

    Uses navigation.list_directory() for recursive traversal.
    Implements Windows wildcards support: *, ?
    Case insensitive by default (Windows behavior).
    Uses analysis.count_files() for progress tracking.

    Args:
        pattern: Search pattern with wildcards
        path: Starting path for search
        case_sensitive: Case sensitivity flag (default False for Windows)

    Returns:
        List of found file paths
    """
    results = []

    def search_recursive(current_path: str) -> None:
        """Recursive search in subdirectories"""
        success, items = navigation.list_directory(current_path)
        if not success:
            return

        for item in items:
            full_path = os.path.join(current_path, item['name'])

            if item['type'] == 'file':
                filename = item['name']

                regex_pattern = '^' + \
                    re.escape(pattern).replace(
                        '\\*', '.*').replace('\\?', '.') + '$'

                if not case_sensitive:
                    regex_pattern = f'(?i){regex_pattern}'

                if re.match(regex_pattern, filename):
                    results.append(full_path)

            elif item['type'] == 'dir':
                try:
                    search_recursive(full_path)
                except (PermissionError, OSError):
                    continue

    search_recursive(path)
    return results


def find_by_windows_extension(extensions: List[str], path: str) -> List[str]:
    """
    Search files by list of Windows extensions.

    Uses analysis.analyze_windows_file_types() for optimization.
    Supports multiple extensions: ['.exe', '.msi', '.dll']
    Automatically adds dot if needed.

    Args:
        extensions: List of file extensions
        path: Starting path for search

    Returns:
        List of found file paths
    """
    results = []

    normalized_exts = []
    for ext in extensions:
        if not ext.startswith('.'):
            ext = '.' + ext
        normalized_exts.append(ext.lower())

    def search_recursive(current_path: str):
        """Recursive search by extensions"""
        success, items = navigation.list_directory(current_path)
        if not success:
            return

        for item in items:
            full_path = os.path.join(current_path, item['name'])

            if item['type'] == 'file':
                _, ext = os.path.splitext(item['name'])
                ext = ext.lower()

                if ext in normalized_exts:
                    results.append(full_path)

            elif item['type'] == 'dir':
                try:
                    search_recursive(full_path)
                except (PermissionError, OSError):
                    continue

    search_recursive(path)
    return results


def find_large_files_windows(min_size_mb: float, path: str) \
        -> List[Dict[str, Any]]:
    """
    Search for large files in Windows file system.

    Uses analysis.count_bytes() for size calculations.

    Args:
        min_size_mb: Minimum size in megabytes
        path: Starting path for search

    Returns:
        List of dictionaries with file information:
        [{'path': '...', 'size_mb': 150.5, 'type': '.zip'}, ...]
    """
    results = []
    min_size_bytes = min_size_mb * 1024 * 1024

    def _search_recursive(current_path: str):
        """Recursive search for large files"""
        success, items = navigation.list_directory(current_path)
        if not success:
            return

        for item in items:
            full_path = os.path.join(current_path, item['name'])

            if item['type'] == 'file' and item['size'] >= min_size_bytes:
                _, ext = os.path.splitext(item['name'])

                results.append({
                    'path': full_path,
                    'size_mb': item['size'] / (1024 * 1024),
                    'size_bytes': item['size'],
                    'type': ext.lower(),
                    'modified': item['modified']
                })

            elif item['type'] == 'dir':
                try:
                    _search_recursive(full_path)
                except (PermissionError, OSError):
                    continue

    _search_recursive(path)
    results.sort(key=lambda x: x['size_bytes'], reverse=True)
    return results


def find_windows_system_files(path: str) -> List[str]:
    """
    Search for Windows system files.

    Finds files typical for Windows system:
    .exe, .dll, .sys in Windows, System32, etc. directories.
    Uses navigation.get_windows_special_folders().

    Args:
        path: Starting path for search

    Returns:
        List of found system file paths
    """
    results = []

    system_extensions = {'.exe', '.dll',
                         '.sys', '.drv', '.ocx', '.cpl', '.msi'}

    system_dirs = {'windows', 'system32', 'system',
                   'program files', 'program files (x86)'}

    def _search_recursive(current_path: str):
        """Recursive search for system files"""
        success, items = navigation.list_directory(current_path)
        if not success:
            return

        for item in items:
            full_path = os.path.join(current_path, item['name'])

            if item['type'] == 'file':
                _, ext = os.path.splitext(item['name'])
                ext = ext.lower()

                path_lower = current_path.lower()
                is_in_system_dir = any(
                    system_dir in path_lower for system_dir in system_dirs)

                if ext in system_extensions or is_in_system_dir:
                    results.append(full_path)

            elif item['type'] == 'dir':
                try:
                    _search_recursive(full_path)
                except (PermissionError, OSError):
                    continue

    _search_recursive(path)
    return results


def search_menu_handler(current_path: str) -> bool:
    """
    Search menu handler for Windows.

    Implements interactive menu using ALL search functions.
    Uses match case for menu navigation.
    Integrates analysis functions to show search statistics.

    Args:
        current_path: Current path

    Returns:
        True if user wants to continue search, False otherwise
    """
    print("\n" + "="*50)
    print(ru_local.SEARCH["menu_title"])
    print("="*50)
    print(f"{ru_local.SEARCH['current_path']}: {current_path}")
    print(f"\n{ru_local.MENU['available_commands']}:")
    print(f"1. {ru_local.SEARCH['cmd_pattern']}")
    print(f"2. {ru_local.SEARCH['cmd_extension']}")
    print(f"3. {ru_local.SEARCH['cmd_large']}")
    print(f"4. {ru_local.SEARCH['cmd_system']}")
    print(f"5. {ru_local.SEARCH['cmd_stats']}")
    print(f"0. {ru_local.SEARCH['cmd_back']}")

    while True:
        try:
            choice = input(f"\n{ru_local.SEARCH['select_command']}: ").strip()

            match choice:
                case "1":
                    pattern = input(
                        f"{ru_local.SEARCH['enter_pattern']}: ").strip()
                    if pattern:
                        results = find_files_windows(pattern, current_path)
                        format_windows_search_results(results, "pattern")
                    else:
                        print(ru_local.SEARCH["pattern_empty"])

                case "2":
                    exts_input = input(
                        f"{ru_local.SEARCH['enter_extensions']}: ").strip()
                    if exts_input:
                        extensions = [ext.strip()
                                      for ext in exts_input.split(',')]
                        results = find_by_windows_extension(
                            extensions, current_path)
                        format_windows_search_results(results, "extension")
                    else:
                        print("❌ Need to specify at least one extension")

                case "3":
                    try:
                        min_size = float(
                            input(f"{ru_local.SEARCH['enter_min_size']}: ").strip())
                        if min_size > 0:
                            results = find_large_files_windows(
                                min_size, current_path)
                            format_windows_search_results(
                                results, "large_files")
                        else:
                            print(ru_local.SEARCH["positive_size"])
                    except ValueError:
                        print(ru_local.SEARCH["valid_number"])

                case "4":
                    print(ru_local.SEARCH["searching_system"])
                    results = find_windows_system_files(current_path)
                    format_windows_search_results(results, "system_files")

                case "5":
                    analysis.show_windows_directory_stats(current_path)

                case "0":
                    return True

                case _:
                    print(ru_local.MENU["invalid_command"])

            cont = input(
                f"\n{ru_local.SEARCH['continue_search']}: ").strip().lower()
            if cont != 'y':
                return True

        except KeyboardInterrupt:
            print(f"\n\n{ru_local.SEARCH['search_interrupted']}")
            return True
        except Exception as e:
            print(f"{ru_local.SEARCH['search_error']}: {e}")
            return False


def format_windows_search_results(results: List, search_type: str) -> None:
    """
    Formatted output of search results for Windows.

    Uses utils.format_size() for file sizes.
    Shows file attributes via analysis.get_windows_file_attributes_stats().

    Args:
        results: Search results
        search_type: Type of search performed
    """
    if not results:
        print(f"\n{ru_local.SEARCH['no_files']}")
        return

    print(f"\n{'='*60}")

    print(
        f"{ru_local.SEARCH['files_found']}: {len(results)} "
        f"{ru_local.SEARCH['files_suffix']}")

    print('='*60)

    if search_type == "large_files":
        print(
            f"{ru_local.SEARCH['path']:<40} {ru_local.SEARCH['size']:>12} "
            f"{ru_local.SEARCH['type']:<8}")
        print('-'*60)

        for item in results:
            path = item['path']
            size_str = utils.format_size(item['size_bytes'])
            file_type = item['type']

            if len(path) > 37:
                path = "..." + path[-37:]

            print(f"{path:<40} {size_str:>12} {file_type:<8}")

    elif search_type in ["pattern", "extension", "system_files"]:
        for i, path in enumerate(results, 1):
            try:
                size = os.path.getsize(path)
                size_str = utils.format_size(size)
                print(f"{i:3d}. {path} ({size_str})")
            except:
                print(f"{i:3d}. {path}")

    print('='*60)
