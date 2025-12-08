import os
import platform
from pathlib import Path
from typing import Union, List, Tuple

PathString = Union[str, Path]


def is_windows_os() -> bool:
    return platform.system() == "Windows"


def validate_windows_path(path: PathString) -> Tuple[bool, str]:
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


def format_size(size_bytes) -> str:
    if size_bytes < 1024:
        return f'{size_bytes} Bytes'
    elif size_bytes < 1024 * 1024:
        return f'{size_bytes / 1024:.2f} KB'
    elif size_bytes < 1024 * 1024 * 1024:
        return f'{size_bytes / (1024 * 1024):.2f} MB'
    else:
        return f'{size_bytes / (1024 * 1024 * 1024):.2f} GB'


def get_parent_path(path: PathString) -> str:
    path_obj = Path(path)
    parent = path_obj.parent
    return str(parent)


def safe_windows_listdir(path: PathString) -> List[str]:
    try:
        return os.listdir(path)
    except PermissionError:
        print('Error: Permission denied')
        return []
    except FileNotFoundError:
        print('Error: File not found')
        return []
    except OsError as e:
        print(f'OsError: {e}')
        return []


def is_hidden_windows_file(path: PathString) -> bool:
    try:
        attrs = os.stat(path).st_file_attributes
        return bool(attrs & 0x02)
    except (AttributeError, OSError):
        return Path(path).name.startswith('.')


print(validate_windows_path('C:\Program Files\Microsoft/ Update Health Tools'))
