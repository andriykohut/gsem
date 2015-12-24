import argparse

from gsem.config import API_ROOT
from gsem.extension import ExtensionManager


def parse_args():
    """Parse command line arguments.

    :returns: argparse.Namespace with parsed args

    """
    parser = argparse.ArgumentParser()
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
    install.add_argument('uuid', help='extension uuid', metavar='UUID')
    reinstall = commands.add_parser('reinstall', help='reinstall extension')
    reinstall.add_argument('uuid', help='extension uuid', metavar='UUID')
    uninstall = commands.add_parser('uninstall', help='uninstall extension')
    uninstall.add_argument('uuid', help='extension uuid', metavar='UUID')
    commands.add_parser('update', help='update extensions')
    return parser.parse_args()


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


def main():
    """Main cli function."""
    args = parse_args()
    manager = ExtensionManager()
    list_cmd_map = {
        'ls': manager.installed,
        'enabled': manager.enabled,
        'disabled': manager.disabled,
        'outdated': manager.outdated,
    }
    if args.cmd in list_cmd_map.keys():
        if args.cmd == 'outdated':
            l = ["{} {} -> {}".format(e.meta['uuid'], e.meta['version'], e.remote_meta['version']) for e in manager.outdated()]
        else:
            l = ["{}@{}".format(e.uuid, e.meta['version']) for e in list_cmd_map[args.cmd]()]
        print("{} ({})".format(manager.ext_dir, len(l)))
        print_nice_list(l)
