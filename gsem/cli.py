import argparse

from gsem.config import API_ROOT

def parse_args():
    """Parse command line arguments.

    :returns: argparse.Namespace with parsed args

    """
    parser = argparse.ArgumentParser()
    commands = parser.add_subparsers()
    commands.add_parser('ls', help='list installed extensions')
    commands.add_parser('enabled', help='list enabled extensions')
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
    update = commands.add_parser('update', help='update extensions')
    return parser.parse_args()


def main():
    """Main cli function."""
    args = parse_args()
