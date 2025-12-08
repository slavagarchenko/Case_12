import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Tuple
from string import ascii_uppercase
import utils


def get_current_drive() -> str:
    """
        Returns the current working drive letter.

        Returns:
            The drive letter of the current working directory (e.g., 'C:').
        """
    cwd = os.getcwd()
    drive, _ = os.path.splitdrive(cwd)
    return drive


def list_available_drives() -> List[str]:
    """
        Lists all available drives on the Windows system.

        Returns:
            A list of available drive letters (e.g., ['C:', 'D:', 'E:']).
        """
    drives = []
    for letter in ascii_uppercase:
        path = f'{letter}:\\'
        if os.path.exists(path):
            drives.append(f'{letter}:')
    return drives


def list_directory(path: str) \
        -> Tuple[bool, List[Dict[str, Any]]]:
    """
      Lists the contents of a directory with file/directory metadata.

      Args:
          path: The directory path to list.

      Returns:
          A tuple containing:
          - success flag (True if directory was successfully read)
          - list of dictionaries with metadata for each entry (name, type, size, modification time, hidden status)
      """
    try:
        entries = utils.safe_windows_listdir(path)
    except Exception:
        return False, []

    result = []

    for name in sorted(entries, key=str.lower):
        full_path = os.path.join(path, name)
        is_dir = os.path.isdir(full_path)

        try:
            stat = os.stat(full_path)
            size = stat.st_size if not is_dir else 0
            modified = (datetime.fromtimestamp(stat.st_mtime).strftime
                (
                '%Y-%m-%d %H:%M:%S'
            ))
        except (OSError, PermissionError):
            size = 0
            modified = 'N/A'

        hidden = utils.is_hidden_windows_file(full_path)

        result.append({
            'name': name,
            'type': 'dir' if is_dir else 'file',
            'size': size,
            'modified': modified,
            'hidden': hidden
        })

    return True, result



def format_directory_output(items: List[Dict[str, Any]]) -> None:
    """
       Formats and prints directory contents in a human-readable table.

       Args:
           items: List of directory entry dictionaries from list_directory().
       """
    print(f"{'Name':<50} {'Type':<6} {'Size':>12} {'Modified':<20} {'Hidden':<6}")
    print('-' * 100)

    if not items:
        print('(пусто)')
        return

    for it in items:
        name = it['name']
        typ = it['type']
        size = it['size']
        modified = it['modified']
        hidden = it['hidden']

        size_str = '-' if typ == 'dir' else utils.format_size(size)
        hidden_str = 'Yes' if hidden else 'No'
        name_display = (name[:47] + '...') if len(name) > 50 else name

        print(f'{name_display:<50} {typ:<6} {size_str:>12} {modified:<20} {hidden_str:<6}')


def move_up(current_path: str) -> str:
    """
        Moves up one directory level from the current path.

        Args:
            current_path: The current directory path.

        Returns:
            The parent directory path, or the same path if already at the root.
        """
    parent = utils.get_parent_path(current_path)
    if Path(parent).resolve() == Path(current_path).resolve():
        return current_path
    return parent


def move_down(current_path: str, target_dir: str) -> Tuple[bool, str]:
    """
       Moves down into a subdirectory from the current path.

       Args:
           current_path: The current directory path.
           target_dir: Name of the subdirectory to enter.

       Returns:
           A tuple containing:
           - success flag (True if successfully entered the subdirectory)
           - the new current path (or unchanged path on failure)
       """
    entries = utils.safe_windows_listdir(current_path)
    if target_dir not in entries:
        return False, current_path

    new_path = os.path.join(current_path, target_dir)
    if not os.path.isdir(new_path):
        return False, current_path

    return True, new_path


def get_windows_special_folders() -> Dict[str, str]:
    """
        Gets the paths of common Windows special folders for the current user.

        Returns:
            A dictionary mapping folder names to their full paths:
            - 'Desktop': User's desktop directory
            - 'Documents': User's documents directory
            - 'Downloads': User's downloads directory
        """
    user_profile = os.environ.get('USERPROFILE')
    return {
        'Desktop': os.path.join(user_profile, 'Desktop'),
        'Documents': os.path.join(user_profile, 'Documents'),
        'Downloads': os.path.join(user_profile, 'Downloads')
    }
