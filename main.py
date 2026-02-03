"""
Main Program Module - Integration of all modules
Developer: System Architect
Dependencies: Uses functions from ALL modules (utils, navigation, analysis, search)
"""

import os
import sys
from typing import NoReturn
import utils
import navigation
import analysis
import search
import ru_local


def check_windows_environment() -> bool:
    """
    Check that program is running in Windows environment.

    Uses utils.is_windows_os().
    If not Windows - displays message and terminates program.

    Returns:
        True if environment is correct
    """
    if not utils.is_windows_os():
        print(ru_local.SYSTEM["windows_required"])
        print(f"{ru_local.SYSTEM['current_os']}: {platform.system()}")
        return False

    print(ru_local.SYSTEM["os_check_passed"])
    return True


def display_windows_banner() -> None:
    """Display banner with Windows information"""
    print("\n" + "="*60)
    print(ru_local.SYSTEM["program_title"])
    print("="*60)

    current_drive = navigation.get_current_drive()
    print(f"{ru_local.SYSTEM['current_drive']}: {current_drive}")

    drives = navigation.list_available_drives()
    print(f"{ru_local.SYSTEM['available_drives']}: {', '.join(drives)}")

    try:
        special_folders = navigation.get_windows_special_folders()
        print(
            f"{ru_local.SYSTEM['special_folders']}: {', '.join(special_folders.keys())}")

    except:
        pass

    print("="*60 + "\n")


def display_main_menu(current_path: str) -> None:
    """
    Display main menu for Windows.

    Shows current path and available commands.
    Uses navigation.list_available_drives() to show drives.
    Integrates options from all modules.

    Args:
        current_path: Current directory path
    """
    print("\n" + "="*60)
    print(ru_local.MENU["main_title"])
    print("="*60)
    print(f"{ru_local.MENU['current_path']}: {current_path}")
    print(f"\n{ru_local.MENU['available_commands']}:")
    print("="*60)
    print(f"{ru_local.MENU['navigation_title']}:")
    print(f"  1. {ru_local.MENU['cmd_show_contents']}")
    print(f"  2. {ru_local.MENU['cmd_enter_subdir']}")
    print(f"  3. {ru_local.MENU['cmd_go_parent']}")
    print(f"  4. {ru_local.MENU['cmd_change_drive']}")
    print(f"  5. {ru_local.MENU['cmd_special_folder']}")
    print(f"  6. {ru_local.MENU['cmd_show_drives']}")

    print(f"\n{ru_local.MENU['analysis_title']}:")
    print(f"  7. {ru_local.MENU['cmd_full_stats']}")
    print(f"  8. {ru_local.MENU['cmd_count_files']}")
    print(f"  9. {ru_local.MENU['cmd_count_size']}")
    print(f" 10. {ru_local.MENU['cmd_analyze_types']}")
    print(f" 11. {ru_local.MENU['cmd_file_attrs']}")

    print(f"\n{ru_local.MENU['search_title']}:")
    print(f" 12. {ru_local.MENU['cmd_search_menu']}")

    print(f"\n{ru_local.MENU['system_title']}:")
    print(f" 13. {ru_local.MENU['cmd_validate_path']}")
    print(f"  0. {ru_local.MENU['cmd_exit']}")
    print("="*60)


def handle_windows_navigation(command: str, current_path: str) -> str:
    """
    Handle navigation commands in Windows.

    Uses navigation.move_up() and navigation.move_down().
    Handles drive changes via navigation.list_available_drives().

    Args:
        command: Command number
        current_path: Current path

    Returns:
        New current path
    """
    match command:
        case "1":
            print(
                f"\n{ru_local.NAVIGATION['directory_contents']} {current_path}:")
            print("-"*60)
            success, items = navigation.list_directory(current_path)

            if success:
                navigation.format_directory_output(items)

            else:
                print(ru_local.NAVIGATION["failed_read_dir"])

            return current_path

        case "2":
            target = input(f"{ru_local.NAVIGATION['enter_subdir']}: ").strip()

            if target:
                success, new_path = navigation.move_down(current_path, target)
                if success:
                    print(f"{ru_local.NAVIGATION['moved_to']}: {new_path}")
                    return new_path

                else:
                    print(f"{ru_local.NAVIGATION['failed_move']} '{target}'")

            return current_path

        case "3":
            new_path = navigation.move_up(current_path)

            if new_path != current_path:
                print(f"{ru_local.NAVIGATION['moved_parent']}: {new_path}")

            else:
                print(ru_local.NAVIGATION["already_root"])

            return new_path

        case "4":
            drives = navigation.list_available_drives()
            print(
                f"{ru_local.SYSTEM['available_drives']}: {', '.join(drives)}")
            drive = input(
                f"{ru_local.NAVIGATION['enter_drive_letter']}: ").strip().upper()

            if drive and f"{drive}:" in drives:
                new_path = f"{drive}:\\"
                print(f"{ru_local.NAVIGATION['moved_drive']} {drive}:\\")
                return new_path

            else:
                print(ru_local.NAVIGATION["invalid_drive"])

            return current_path

        case "5":
            folders = navigation.get_windows_special_folders()
            print(f"{ru_local.SYSTEM['special_folders']} Windows:")

            for i, (name, path) in enumerate(folders.items(), 1):
                print(f"  {i}. {name}: {path}")

            try:
                choice = int(
                    input(f"{ru_local.NAVIGATION['select_special_folder']}: ").strip())
                if 1 <= choice <= len(folders):
                    folder_names = list(folders.keys())
                    selected = folder_names[choice-1]
                    new_path = folders[selected]

                    if os.path.exists(new_path):
                        print(f"✅ Перешел в {selected}: {new_path}")
                        return new_path

                    else:
                        print(f"{ru_local.NAVIGATION['folder_not_exist']}")

            except (ValueError, IndexError):
                print(ru_local.NAVIGATION["invalid_selection"])

            return current_path

        case "6":
            drives = navigation.list_available_drives()
            print(
                f"{ru_local.SYSTEM['available_drives']}: {', '.join(drives)}")

            return current_path

        case _:
            return current_path


def handle_windows_analysis(command: str, current_path: str) -> None:
    """
    Handle Windows file system analysis commands.

    Uses analysis.show_windows_directory_stats()
    and other analysis functions.

    Args:
        command: Command number
        current_path: Current path
    """
    match command:
        case "7":
            print(f"\n📊 {ru_local.ANALYSIS['full_stats']}: {current_path}")
            analysis.show_windows_directory_stats(current_path)

        case "8":
            print(f"\n📄 {ru_local.ANALYSIS['count_files']}: {current_path}")
            success, count = analysis.count_files(current_path)

            if success:
                print(f"✅ {ru_local.ANALYSIS['files_found']}: {count}")

            else:
                print(ru_local.ANALYSIS["count_error"])

        case "9":
            print(f"\n💾 {ru_local.ANALYSIS['count_size']}: {current_path}")
            success, size = analysis.count_bytes(current_path)

            if success:
                print(
                    f"✅ {ru_local.ANALYSIS['total_size']}: {utils.format_size(size)}")

            else:
                print(ru_local.ANALYSIS["size_error"])

        case "10":
            print(f"\n📋 {ru_local.ANALYSIS['analyze_types']}: {current_path}")
            success, types = analysis.analyze_windows_file_types(current_path)

            if success and types:
                print(ru_local.ANALYSIS["file_types"])

                for ext, info in sorted(types.items(), key=lambda x: -x[1]['bytes']):
                    if info['count'] > 0:
                        ext_display = ext if ext else ru_local.ANALYSIS["no_extension"]
                        print(
                            f"  {ext_display}: {info['count']} {ru_local.ANALYSIS['files']}, {utils.format_size(info['bytes'])}")

            elif not types:
                print(ru_local.ANALYSIS["no_files"])

            else:
                print(ru_local.ANALYSIS["types_error"])

        case "11":
            print(f"\n🔒 {ru_local.ANALYSIS['attrs_stats']}: {current_path}")
            stats = analysis.get_windows_file_attributes_stats(current_path)
            print(f"  {ru_local.ANALYSIS['hidden_files']}: {stats['hidden']}")
            print(f"  {ru_local.ANALYSIS['system_files']}: {stats['system']}")
            print(
                f"  {ru_local.ANALYSIS['readonly_files']}: {stats['readonly']}")


def handle_windows_search(command: str, current_path: str) -> str:
    """
    Handle Windows search commands.

    Uses search.search_menu_handler().

    Args:
        command: Command number
        current_path: Current path

    Returns:
        Updated path (may change after search)
    """
    if command == "12":
        print(
            f"\n🔍 {ru_local.SEARCH['menu_title']} ({ru_local.SEARCH['current_path']}: {current_path})")
        continue_search = search.search_menu_handler(current_path)
        return current_path

    return current_path


def run_windows_command(command: str, current_path: str) -> str:
    """
    Main command handler using match case.

    Integrates ALL modules:
    - navigation for commands 1, 5, 6
    - analysis for commands 2, 4  
    - search for command 3

    Args:
        command: User command
        current_path: Current path

    Returns:
        Updated current path
    """
    if command not in ["0", "13"]:
        is_valid, error_msg = utils.validate_windows_path(current_path)

        if not is_valid:
            print(
                f"{ru_local.VALIDATION['invalid_path_warning']}: {error_msg}")
            print(ru_local.VALIDATION["go_valid_dir"])
            return current_path

    match command:
        case "1" | "2" | "3" | "4" | "5" | "6":
            return handle_windows_navigation(command, current_path)

        case "7" | "8" | "9" | "10" | "11":
            handle_windows_analysis(command, current_path)
            return current_path

        case "12":
            return handle_windows_search(command, current_path)

        case "13":
            is_valid, msg = utils.validate_windows_path(current_path)

            if is_valid:
                print(f"{ru_local.VALIDATION['path_valid']}: {current_path}")

            else:
                print(f"{ru_local.VALIDATION['path_invalid']}: {msg}")

            return current_path

        case _:

            if command != "0":
                print(ru_local.MENU["invalid_command"])

            return current_path


def main() -> None:
    """
    Main program function for Windows.

    Steps:
    1. Check Windows environment
    2. Show banner
    3. Main loop while command != "0"
    4. Error handling and termination
    """
    if not check_windows_environment():
        print(ru_local.SYSTEM["press_enter_exit"])
        input()
        sys.exit(1)

    display_windows_banner()

    current_path = os.getcwd()
    print(f"📁 {ru_local.MENU['current_path']}: {current_path}")

    command = None

    while command != "0":
        display_main_menu(current_path)
        command = input(f"\n{ru_local.MENU['enter_command']}: ").strip()

        if command != "0":
            current_path = run_windows_command(command, current_path)
        else:
            print("\n" + "="*60)
            print(ru_local.SYSTEM["thanks"])
            print("="*60)

    print(f"\n{ru_local.SYSTEM['press_enter_exit']}")
    input()
    sys.exit(0)


if __name__ == "__main__":
    main()
