import os
from gsem.utils import gnome_shell_version

EXTENSION_DIR = os.path.expanduser(
    '~/.local/share/gnome-shell/extensions'
)
GNOME_SHELL_VERSION = gnome_shell_version()

API_ROOT = 'https://extensions.gnome.org'
API_DETAIL = API_ROOT + '/ajax/detail'
API_SEARCH = API_ROOT + '/extension-query'
