#!/usr/bin/env python3
import os
import argparse
import json
import subprocess
import urllib.parse
import urllib.request
from gi.repository import Gio

EXTENSION_DIR = os.path.join(
        os.path.expanduser("~/.local/share/gnome-shell/extensions")
)

EXTENSIONS_API = 'https://extensions.gnome.org/ajax/detail'
DOWNLOAD_URL = 'https://extensions.gnome.org/static/extension-data'
SEARCH_URL = 'https://extensions.gnome.org/extension-query'

def build_download_url(uuid, version):
    uri = urllib.parse.quote(
        '{}.v{}.shell-extension.zip'.format(uuid, version)
    )
    return "{}/{}".format(DOWNLOAD_URL, uri)


def get_gnome_version():
    proc = subprocess.Popen(
            ['gnome-shell', '--version'],
            stdout=subprocess.PIPE
    )
    out = proc.communicate()[0]
    version_str = out.split()[-1].decode('utf-8')
    return [int(v) for v in version_str.split('.')]

GNOME_VERSION = get_gnome_version()

def get_args():
    parser = argparse.ArgumentParser()
    cmd = parser.add_subparsers(dest='cmd')
    cmd.add_parser('ls', help='List installed extensions')
    cmd.add_parser('check', help='Check for updates')
    info = cmd.add_parser('info', help='Show extension info')
    info.add_argument('uuid', help='Show extention information')
    search = cmd.add_parser('search', help='Search for extensions')
    search.add_argument('term', help='Search term')
    return parser.parse_args()


def get_extensions(extension_dir):
    found = next(os.walk(extension_dir))[1]
    for extension in found:
        meta_path = os.path.join(extension_dir, extension, 'metadata.json')
        try:
            with open(meta_path) as mf:
                yield json.load(mf)
        except Exception as e:
            print(e)


def ls():
    for ext in get_extensions(EXTENSION_DIR):
        print("{} [{}]".format(ext['name'], ext['version']))


def check():
    for ext in get_extensions(EXTENSION_DIR):
        params = urllib.parse.urlencode({
            'uuid': ext['uuid'],
            'version': ext['version']
        })
        url = "{}/?{}".format(EXTENSIONS_API, params)
        patch_version = '{}.{}'.format(GNOME_VERSION[0], GNOME_VERSION[1])
        minor_version = '{}.{}.{}'.format(*GNOME_VERSION)
        remote_version = None
        with urllib.request.urlopen(url) as f:
            data = json.loads(f.read().decode('utf-8'))
        try:
            remote_version = data['shell_version_map'][minor_version]['version']
        except KeyError:
            try:
                remote_version = data['shell_version_map'][patch_version]['version']
            except KeyError:
                print("Extension {} not found".format(ext['name']))
                continue
        if remote_version and (remote_version > ext['version']):
            print("{} requires update (local: {}, remote: {})".format(ext['name'], ext['version'], remote_version))


def search(term):
    params = urllib.parse.urlencode({
        'shell_version': '{}.{}.{}'.format(*GNOME_VERSION),
        'search': term,
    })
    with urllib.request.urlopen("{}/?{}".format(SEARCH_URL, params)) as f:
        data = json.loads(f.read().decode('utf-8'))
    installed_extensions = get_extensions(EXTENSION_DIR)
    uuid_map = dict((e['uuid'], e) for e in installed_extensions)
    for ext in data['extensions']:
        if ext['uuid'] in uuid_map:
            print("{} ✔".format(ext['name']))
        else:
            print(ext['name'])


def enabled():
    # TODO: use gsettings to get enabled extensions
    pass


def enable(extension):
    # TODO: use gsettings to enable extension
    pass


def disable(extension):
    # TODO: use gsettings to disable extension
    pass


def install(uuid):
    # TODO: install extension
    pass


def uninstall(uuid):
    # TODO: uninstall extension
    pass


def reinstall(extension):
    # TODO: reinstall
    pass


def main():
    args = get_args()
    if args.cmd == 'ls':
        ls()
    elif args.cmd == 'check':
        check()
    elif args.cmd == 'search':
        search(args.term)
if __name__ == "__main__":
    main()
