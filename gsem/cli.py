import argparse

from gsem.config import API_ROOT
from gsem.config import EXTENSION_DIR
from gsem.extension import Extension
from gsem.extension import ExtensionManager
from gsem.utils import reload_gnome_shell


def cli_args():
    """Parse command line arguments.

    :returns: argparse.Namespace with parsed args

    """
    parser = argparse.ArgumentParser(description='Gnome-Shell extension manager')
    commands = parser.add_subparsers(dest='cmd')
    commands.add_parser('ls', help='list installed extensions')
    commands.add_parser('enabled', help='list enabled extensions')
    commands.add_parser('disabled', help='list disabled extensions')
    commands.add_parser('outdated', help='list outdated extensions')
    info = commands.add_parser('info', help='show extension information')
    info.add_argument('uuid', help='extension uuid', metavar='UUID')
    info.add_argument('-r', '--remote', help='fetch info from {}'.format(API_ROOT),
                      action='store_true', default=False)
    install = commands.add_parser('install', help='install extension')
    install.add_argument('uuid', help='extension uuid')
    install.add_argument('--disabled', help='do not enable the extension', default=False,
                         action='store_true', dest='disabled')
    install.add_argument('--no-reload', help='do not reload gnome-shell', default=False,
                         action='store_true', dest='no_reload')
    reinstall = commands.add_parser('reinstall', help='reinstall extension')
    reinstall.add_argument('uuid', help='extension uuid', metavar='UUID')
    uninstall = commands.add_parser('uninstall', help='uninstall extension')
    uninstall.add_argument('uuid', help='extension uuid', metavar='UUID')
    commands.add_parser('update', help='update extensions')
    search = commands.add_parser('search', help='search extensions')
    search.add_argument('term', help='search term', metavar='TERM')
    enable = commands.add_parser('enable', help='enable extension')
    enable.add_argument('uuid', help='extension uuid', metavar='UUID')
    disable = commands.add_parser('disable', help='disable extension')
    disable.add_argument('uuid', help='extensions uuid', metavar='UUID')
    return parser


def print_nice_list(l):
    """Nicely print list.

    :l: list to print

    """
    length = len(l)
    for index, item in enumerate(l):
        if index < length-1:
            print('├── {}'.format(item))
        else:
            print('└── {}'.format(item))


def print_info(ext):
    """Print extension info.

    :ext: gsem.extension.Extension object

    """
    print("{} - ({})".format(ext.remote_meta['name'], ext.uuid))
    print()
    if ext.installed():
        if ext.outdated():
            print('outdated: {} -> {}'.format(ext.meta['version'], ext.remote_meta['version']))
        else:
            print('up to date: {}'.format(ext.meta['version']))
    else:
        print('not installed: {}'.format(ext.remote_meta['version']))
    print()
    print(ext.remote_meta['description'])


def main():
    # TODO: This is ugly!
    """Main cli function."""
    parser = cli_args()
    args = parser.parse_args()
    if not args.cmd:
        parser.print_usage()
        parser.exit(1)
    manager = ExtensionManager()
    list_cmd_map = {
        'ls': manager.installed,
        'enabled': manager.enabled,
        'disabled': manager.disabled,
        'outdated': manager.outdated,
        'disabled': manager.disabled,
        'search': lambda: manager.search(args.term),
    }
    if args.cmd in list_cmd_map.keys():
        result = list_cmd_map[args.cmd]()
        if args.cmd == 'outdated':
            print("{} ({})".format(manager.ext_dir, len(result)))
            l = ["{} {} -> {}".format(e.meta['uuid'], e.meta['version'], e.remote_meta['version']) for e in result]
        if args.cmd == 'search':
            print("Search results for '{}' ({})".format(args.term, len(result)))
            l = ['{} - {}'.format(e.remote_meta['uuid'], e.remote_meta['name']) for e in result]
        else:
            l = ["{}@{}".format(e.uuid, e.meta['version']) for e in result]
            print("{} ({})".format(manager.ext_dir, len(l)))
        print_nice_list(l)
    elif args.cmd == 'info':
        print_info(Extension(args.uuid))
    elif args.cmd == 'enable':
        enabled = manager.enable(args.uuid)
        if enabled:
            print("'{}' enabled".format(args.uuid))
        else:
            print("Can't enable '{}'".format(args.uuid))
    elif args.cmd == 'disable':
        disabled = manager.disable(args.uuid)
        if disabled:
            print("'{}' disabled".format(args.uuid))
        else:
            print("Can't disable '{}".format(args.uuid))
    elif args.cmd == 'install':
        if args.uuid in manager.installed_uuids():
            print("'{}' already installed".format(args.uuid))
        else:
            print("Installing {} to '{}'".format(args.uuid, EXTENSION_DIR))
            manager.install(args.uuid)
            if not args.disabled:
                print("Enabling '{}'".format(args.uuid))
                manager.enable(args.uuid)
                if not args.no_reload:
                    print("Reloading gnome-shell...")
                    reload_gnome_shell()
    elif args.cmd == 'reinstall':
        if args.uuid not in manager.installed_uuids():
            print("'{}' is not installed".format(args.uuid))
        else:
            print("Uninstalling '{}'".format(args.uuid))
            ext = Extension(args.uuid)
            was_enabled = ext.enabled()
            manager.uninstall(args.uuid)
            print("Installing {} to '{}'".format(args.uuid, EXTENSION_DIR))
            manager.install(args.uuid)
            if was_enabled:
                manager.enable(args.uuid)
    elif args.cmd == 'uninstall':
        if args.uuid not in manager.installed_uuids():
            print("'{}' is not installed".format(args.uuid))
        else:
            print("Uninstalling '{}'".format(args.uuid))
            manager.uninstall(args.uuid)
    elif args.cmd == 'update':
        outdated = manager.outdated()
        print('Extension updates avaliable ({})'.format(len(outdated)))
        if outdated:
            l = ["{} {} -> {}".format(e.uuid, e.meta['version'], e.remote_meta['version']) for e in outdated]
            print_nice_list(l)
            prompt = input('Would you like to install these updates? (yes) ')
            if prompt.lower().strip().startswith('y'):
                for e in outdated:
                    was_enabled = e.enabled()
                    print("Installing {}@{} to {}".format(e.uuid, e.remote_meta['version'], EXTENSION_DIR))
                    manager.uninstall(e.uuid)
                    manager.install(e.uuid)
                    if was_enabled:
                        manager.enable(e.uuid)
                reload_gnome_shell()
