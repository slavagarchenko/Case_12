import os
import platform
from pathlib import Path
from typing import Union, List, Tuple

PathString = Union[str, Path]


def is_windows_os() -> bool:
    """
     Checks if the current operating system is Windows.

     Returns:
         True if running on Windows, False otherwise.
     """
    return platform.system() == "Windows"


def validate_windows_path(path: PathString) -> Tuple[bool, str]:
    """
      Validates a Windows path for correctness and existence.

      Args:
          path: The path to validate (string or Path object).

      Returns:
          A tuple containing:
          - validation success flag (True if valid)
          - error message (empty string if valid, description if invalid)
      """
    path_str = str(path)
    forbidden_chars = ['*', '?', '"', '>', '<', '|']

    for char in forbidden_chars:
        if char in path_str:
            return False, 'The char is forbidden'

    if '/' in path_str:
        return False, "Use \\ instead of /"

    if ':' in path_str:
        parts = path_str.split(':')
        if len(parts) != 2:
            return False, 'Incorrect usage of \':\''
        if len(parts[0]) != 1 or not parts[0].isalpha():
            return False, 'Incorrect disks name'

    if len(str(path)) > 260:
        return False, 'Path is too long'

    if not os.path.exists(str(path)):
        return False, 'Path does not exist'
    return True, ''


def format_size(size_bytes: int) -> str:
    """
        Converts a size in bytes to a human-readable string.

        Args:
            size_bytes: Size in bytes (integer or float).

        Returns:
            Formatted string with appropriate unit (Bytes, KB, MB, GB).
        """
    if size_bytes < 1024:
        return f'{size_bytes} Bytes'

    elif size_bytes < 1024 ** 2:
        return f'{size_bytes / 1024:.2f} KB'

    elif size_bytes < 1024 ** 3:
        return f'{size_bytes / (1024 ** 2):.2f} MB'

    else:
        return f'{size_bytes / (1024 ** 3):.2f} GB'


def get_parent_path(path: PathString) -> str:
    """
       Returns the parent directory of the given path.

       Args:
           path: The file or directory path.

       Returns:
           String representation of the parent directory path.
       """
    path_obj = Path(path)
    parent = path_obj.parent
    return str(parent)


def safe_windows_listdir(path: PathString) -> List[str]:
    """
       Safely lists directory contents, handling common errors gracefully.

       Args:
           path: The directory path to list.

       Returns:
           List of directory entry names, or empty list on error.
       """
    try:
        return os.listdir(path)

    except PermissionError:
        print('Error: Permission denied')
        return []

    except FileNotFoundError:
        print('Error: File not found')
        return []

    except OSError as e:
        print(f'OsError: {e}')
        return []


def is_hidden_windows_file(path: PathString) -> bool:
    """
        Checks if a file or directory is hidden on Windows.

        Args:
            path: The file or directory path.

        Returns:
            True if the file/directory has the hidden attribute set, 
            False otherwise.
        """
    try:
        attrs = os.stat(path).st_file_attributes
        return bool(attrs & 0x02)

    except (AttributeError, OSError):
        return Path(path).name.startswith('.')
