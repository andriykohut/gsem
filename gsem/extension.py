import json
import os
import shutil
from gi.repository import Gio
from gi.repository import GLib

from gsem.utils import get_json_response
from gsem.utils import download_and_extract_zip
from gsem.config import (
    EXTENSION_DIR,
    GNOME_SHELL_VERSION,
    API_ROOT,
    API_DETAIL,
    API_SEARCH,
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
            with open(os.path.join(EXTENSION_DIR, self.uuid, 'metadata.json')) as f:
                self._meta = json.load(f)
        return self._meta

    @property
    def remote_meta(self):
        """Remote metadata dict."""
        if not self._remote_meta:
            self._remote_meta = get_json_response(API_DETAIL, {
                'uuid': self.uuid,
                'shell_version': '.'.join(str(v) for v in GNOME_SHELL_VERSION),
            })
        return self._remote_meta

    @remote_meta.setter
    def remote_meta(self, value):
        self.uuid = value['uuid']
        self._remote_meta = value

    def outdated(self):
        # TODO: use https://extensions.gnome.org/update-info/?installed={%22arch-update@RaphaelRochet%22:{%22version%22:6}}&shell_version=3.18.3
        return self.remote_meta['version'] > self.meta['version']

    def enabled(self):
        return self.uuid in (Gio.Settings
                             .new('org.gnome.shell')
                             .get_value('enabled-extensions'))

    def installed(self):
        installed = True
        try:
            self.meta['uuid']
        except FileNotFoundError:
            installed = False
        return installed


class ExtensionManager:

    def __init__(self, ext_dir=EXTENSION_DIR):
        self.ext_dir = ext_dir

    def enabled_uuids(self):
        return set(
            Gio.Settings.new('org.gnome.shell')
            .get_value('enabled-extensions')
        ).intersection({ex.uuid for ex in self.installed()})

    def installed_uuids(self):
        return os.listdir(self.ext_dir)

    def installed(self):
        return [Extension(uuid) for uuid in self.installed_uuids()]

    def enabled(self):
        return [Extension(uuid) for uuid in self.enabled_uuids()]

    def disabled(self):
        installed_uuids = {e.uuid for e in self.installed()}
        enabled_uuids = {e.uuid for e in self.enabled()}
        return [Extension(uuid) for uuid in installed_uuids.difference(enabled_uuids)]

    def outdated(self):
        # TODO: use https://extensions.gnome.org/update-info/?installed={%22arch-update@RaphaelRochet%22:{%22version%22:6}}&shell_version=3.18.3
        return [e for e in self.enabled() if e.outdated()]

    def search(self, term):
        query = {
            'shell_version': '.'.join(str(v) for v in GNOME_SHELL_VERSION),
            'search': term,
        }
        response = get_json_response(API_SEARCH, query)
        found = []
        for remote_meta in response['extensions']:
            ext = Extension(remote_meta['uuid'])
            ext.remote_meta = remote_meta
            found.append(ext)
        return found

    def enable(self, uuid):
        if uuid in self.enabled_uuids():
            return True
        ext = Extension(uuid)
        if not ext.installed():
            return False
        enabled_uuids = self.enabled_uuids()
        enabled_uuids.add(uuid)
        Gio.Settings('org.gnome.shell').set_value(
            'enabled-extensions',
            GLib.Variant('as', list(enabled_uuids))
        )
        return True

    def disable(self, uuid):
        if uuid not in self.installed_uuids():
            raise Extension('Not installed')
        enabled_uuids = self.enabled_uuids()
        if uuid not in enabled_uuids:
            return True
        enabled_uuids.remove(uuid)
        Gio.Settings('org.gnome.shell').set_value(
            'enabled-extensions',
            GLib.Variant('as', list(enabled_uuids))
        )
        return True

    def install(self, uuid):
        ext = Extension(uuid)
        download_url = API_ROOT + ext.remote_meta['download_url']
        dest_dir = os.path.join(EXTENSION_DIR, uuid)
        download_and_extract_zip(download_url, dest_dir)
        return ext

    def uninstall(self, uuid):
        self.disable(uuid)
        shutil.rmtree(os.path.join(EXTENSION_DIR, uuid))
