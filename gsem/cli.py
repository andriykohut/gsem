import argparse
from typing import Callable, Dict, List
from urllib.error import HTTPError

from gsem.config import API_ROOT, EXTENSION_DIR, GNOME_SHELL_VERSION
from gsem.extension import Extension, ExtensionManager
from gsem.utils import reload_gnome_shell


def cli_args() -> argparse.ArgumentParser:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Gnome-Shell extension manager",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    commands = parser.add_subparsers(dest="cmd")
    commands.add_parser("ls", help="list installed extensions")
    commands.add_parser("enabled", help="list enabled extensions")
    commands.add_parser("disabled", help="list disabled extensions")
    commands.add_parser("outdated", help="list outdated extensions")
    info = commands.add_parser("info", help="show extension information")
    info.add_argument("uuid", help="extension uuid", metavar="UUID")
    info.add_argument(
        "-r",
        "--remote",
        help="fetch info from {}".format(API_ROOT),
        action="store_true",
        default=False,
    )
    install = commands.add_parser("install", help="install extension")
    install.add_argument("uuid", help="extension uuid")
    install.add_argument(
        "--disabled",
        help="do not enable the extension",
        default=False,
        action="store_true",
        dest="disabled",
    )
    install.add_argument(
        "--reload",
        help="Reload gnome-shell after installation",
        default=False,
        action="store_true",
        dest="reload",
    )
    reinstall = commands.add_parser("reinstall", help="reinstall extension")
    reinstall.add_argument("uuid", help="extension uuid", metavar="UUID")
    uninstall = commands.add_parser("uninstall", help="uninstall extension")
    uninstall.add_argument("uuid", help="extension uuid", metavar="UUID")
    commands.add_parser("update", help="update extensions")
    search = commands.add_parser("search", help="search extensions")
    search.add_argument("term", help="search term", metavar="TERM")
    search.add_argument(
        "--shell-version",
        dest="shell_version",
        default=".".join([str(v) for v in GNOME_SHELL_VERSION]),
        help="Gnome Shell version",
        type=str,
    )
    enable = commands.add_parser("enable", help="enable extension")
    enable.add_argument("uuid", help="extension uuid", metavar="UUID")
    disable = commands.add_parser("disable", help="disable extension")
    disable.add_argument("uuid", help="extensions uuid", metavar="UUID")
    for command in commands.choices.values():
        command.formatter_class = argparse.ArgumentDefaultsHelpFormatter
    return parser


def print_nice_list(list_: List[str]) -> None:
    """Nicely print list."""
    length = len(list_)
    for index, item in enumerate(list_):
        if index < length - 1:
            print("├── {}".format(item))
        else:
            print("└── {}".format(item))


def print_info(ext: Extension) -> None:
    """Print extension info."""
    print(f"{ext.remote_meta['name']} - ({ext.uuid})")
    print()
    if ext.is_installed:
        if ext.is_outdated:
            print(f"outdated: {ext.version} -> {ext.remote_version}")
        else:
            print(f"up to date: {ext.version}")
    else:
        print(f"not installed: {ext.remote_version}")
    print()
    print(ext.remote_meta["description"])


def main() -> None:
    # TODO: This is ugly!
    """Main cli function."""
    parser = cli_args()
    args = parser.parse_args()
    if not args.cmd:
        parser.print_usage()
        parser.exit(1)
    manager = ExtensionManager()
    list_cmd_map: Dict[str, Callable[[], List[Extension]]] = {
        "disabled": manager.disabled,
        "enabled": manager.enabled,
        "ls": manager.installed,
        "outdated": manager.outdated,
        "search": lambda: manager.search(args.term, args.shell_version),
    }
    if args.cmd in list_cmd_map.keys():
        result = list_cmd_map[args.cmd]()
        if args.cmd == "outdated":
            print(f"{manager.ext_dir} ({len(result)})")
            lines = [
                f"{e.meta['uuid']} {e.version} -> {e.remote_version}" for e in result
            ]
        elif args.cmd == "search":
            print(f"Search results for '{args.term}' ({len(result)})")
            lines = [
                f"{e.remote_meta['uuid']} - {e.remote_meta['name']}" for e in result
            ]
        else:
            lines = [f"{e.uuid}@{e.version}" for e in result]
            print(f"{manager.ext_dir} ({len(lines)})")
        print_nice_list(lines)
    elif args.cmd == "info":
        try:
            print_info(Extension(args.uuid))
        except HTTPError as err:
            if err.code == 404:
                print("Extension not found")
                return
            raise
    elif args.cmd == "enable":
        enabled = manager.enable(args.uuid)
        if enabled:
            print(f"'{args.uuid}' enabled")
        else:
            print(f"Can't enable '{args.uuid}'")
    elif args.cmd == "disable":
        disabled = manager.disable(args.uuid)
        if disabled:
            print(f"'{args.uuid}' disabled")
        else:
            print(f"Can't disable '{args.uuid}'")
    elif args.cmd == "install":
        if args.uuid in manager.installed_uuids():
            print(f"'{args.uuid}' already installed")
        else:
            print(f"Installing {args.uuid} to '{EXTENSION_DIR}'")
            manager.install(args.uuid)
            if not args.disabled:
                print(f"Enabling '{args.uuid}'")
                manager.enable(args.uuid)
                if args.reload:
                    print("Reloading gnome-shell...")
                    reload_gnome_shell()
    elif args.cmd == "reinstall":
        if args.uuid not in manager.installed_uuids():
            print(f"'{args.uuid}' is not installed")
        else:
            print(f"Uninstalling '{args.uuid}'")
            ext = Extension(args.uuid)
            was_enabled = ext.is_enabled
            manager.uninstall(args.uuid)
            print(f"Installing {args.uuid} to '{EXTENSION_DIR}'")
            manager.install(args.uuid)
            if was_enabled:
                manager.enable(args.uuid)
    elif args.cmd == "uninstall":
        if args.uuid not in manager.installed_uuids():
            print(f"'{args.uuid}' is not installed")
        else:
            print(f"Uninstalling '{args.uuid}'")
            manager.uninstall(args.uuid)
    elif args.cmd == "update":
        outdated = manager.outdated()
        print(f"Extension updates available ({len(outdated)})")
        if outdated:
            lines = [f"{e.uuid} {e.version} -> {e.remote_version}" for e in outdated]
            print_nice_list(lines)
            prompt = input("Would you like to install these updates? (yes) ")
            if prompt.lower().strip().startswith("y"):
                for e in outdated:
                    was_enabled = e.is_enabled
                    print(f"Installing {e.uuid}@{e.remote_version} to {EXTENSION_DIR}")
                    manager.uninstall(e.uuid)
                    manager.install(e.uuid)
                    if was_enabled:
                        manager.enable(e.uuid)
                reload_gnome_shell()
