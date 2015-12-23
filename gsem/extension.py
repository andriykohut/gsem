import json
import os
from gi.repository import Gio

from gsem.utils import get_json_response
from gsem.config import (
    EXTENSION_DIR,
    GNOME_SHELL_VERSION,
    API_DETAIL,
)


class Extension:
    def __init__(self, uuid):
        self.uuid = uuid
        self._meta = None
        self._remote_meta = None

    @property
    def meta(self):
        """Local metadata dict."""
        if not self._meta:
            with open(os.path.join(EXTENSION_DIR, self.uuid)) as f:
                self._meta = json.load(f)
        return self._meta

    @property
    def remote_meta(self):
        """Remote metadata dict."""
        if not self._remote_meta:
            self._remote_meta = get_json_response(API_DETAIL, {
                'uuid': self.uuid,
                'shell_version': GNOME_SHELL_VERSION,
            })
        return self._remote_meta

    def outdated(self):
        return self.remote_meta['version'] > self.meta['version']

    def enabled(self):
        return self.uuid in (Gio.Settings
                             .new('org.gnome.shell')
                             .get_value('enabled-extensions'))


class ExtensionManager:

    def enabled_extensions(self):
        return self.gsettings.get_value('enabled-extensions')

    def installed(self):
        for uuid in os.listdir(EXTENSION_DIR):
            yield Extension(uuid)

    def enabled(self):
        for uuid in self.enabled_extensions():
            yield Extension(uuid)
