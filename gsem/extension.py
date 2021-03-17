import json
import os
import shutil
import warnings
from distutils.version import LooseVersion
from typing import List, Optional, Set

from gi.repository import Gio, GLib  # type: ignore

from gsem.config import (
    API_DETAIL,
    API_ROOT,
    API_SEARCH,
    EXTENSION_DIR,
    GNOME_SHELL_VERSION,
)
from gsem.utils import download_and_extract_zip, get_json_response


class Extension:
    """Extension metadata."""

    def __init__(self, uuid: str) -> None:
        self.uuid = uuid
        self._meta: Optional[dict] = None
        self._remote_meta: Optional[dict] = None

    @property
    def meta(self) -> dict:
        """Local metadata dict."""
        if not self._meta:
            with open(os.path.join(EXTENSION_DIR, self.uuid, "metadata.json")) as f:
                self._meta = json.load(f)
        assert self._meta, f"No local metadata for {self.uuid}"
        return self._meta

    @property
    def remote_meta(self) -> dict:
        """Remote metadata dict."""
        if not self._remote_meta:
            self._remote_meta = get_json_response(
                API_DETAIL,
                {
                    "uuid": self.uuid,
                    "shell_version": ".".join(str(v) for v in GNOME_SHELL_VERSION),
                },
            )
        assert self._remote_meta, f"No remote metadata for {self.uuid}"
        return self._remote_meta

    @remote_meta.setter
    def remote_meta(self, value: dict) -> None:
        self.uuid = value["uuid"]
        self._remote_meta = value

    @property
    def version(self) -> LooseVersion:
        return LooseVersion(str(self.meta["version"]))

    @property
    def remote_version(self) -> LooseVersion:
        return LooseVersion(str(self.remote_meta["version"]))

    @property
    def is_outdated(self) -> bool:
        # TODO: use https://extensions.gnome.org/update-info/?installed={%22arch-update@RaphaelRochet%22:{%22version%22:6}}&shell_version=3.18.3  # noqa
        return self.remote_version > self.version

    @property
    def is_enabled(self) -> bool:
        return self.uuid in (
            Gio.Settings.new("org.gnome.shell").get_value("enabled-extensions")
        )

    @property
    def is_installed(self) -> bool:
        try:
            self.meta["uuid"]
            return True
        except FileNotFoundError:
            return False

    @property
    def is_supported(self) -> bool:
        try:
            for f in ["description", "name", "version"]:
                assert f in self.meta, f'Missing field  - "{f}"'
            return True
        except Exception as e:
            warnings.warn(
                f"[{self.uuid}] {e}: metadata {self.meta} - extension is not supported"
            )
            return False


class ExtensionManager:
    def __init__(self, ext_dir: str = EXTENSION_DIR) -> None:
        self.ext_dir = ext_dir

    def enabled_uuids(self) -> Set[str]:
        return set(
            Gio.Settings.new("org.gnome.shell").get_value("enabled-extensions")
        ).intersection(self.installed_uuids())

    def installed_uuids(self) -> List[str]:
        return os.listdir(self.ext_dir)

    def installed(self) -> List[Extension]:
        installed = []
        for uuid in self.installed_uuids():
            ext = Extension(uuid)
            if ext.is_supported:
                installed.append(ext)
        return installed

    def enabled(self) -> List[Extension]:
        return [Extension(uuid) for uuid in self.enabled_uuids()]

    def disabled(self) -> List[Extension]:
        enabled_uuids = {e.uuid for e in self.enabled()}
        return [
            Extension(uuid)
            for uuid in set(self.installed_uuids()).difference(enabled_uuids)
        ]

    def outdated(self) -> List[Extension]:
        # TODO: use https://extensions.gnome.org/update-info/?installed={%22arch-update@RaphaelRochet%22:{%22version%22:6}}&shell_version=3.18.3  # noqa
        return [e for e in self.installed() if e.is_outdated]

    @staticmethod
    def search(term: str, shell_version: str = "all") -> List[Extension]:
        query = {
            "shell_version": shell_version,
            "search": term,
        }
        response = get_json_response(API_SEARCH, query)
        found = []
        for remote_meta in response["extensions"]:
            ext = Extension(remote_meta["uuid"])
            ext.remote_meta = remote_meta
            found.append(ext)
        return found

    def enable(self, uuid: str) -> bool:
        if uuid in self.enabled_uuids():
            return True
        ext = Extension(uuid)
        if not ext.is_installed:
            return False
        enabled_uuids = self.enabled_uuids()
        enabled_uuids.add(uuid)
        Gio.Settings("org.gnome.shell").set_value(
            "enabled-extensions",
            GLib.Variant("as", list(enabled_uuids)),
        )
        return True

    def disable(self, uuid: str) -> bool:
        if uuid not in self.installed_uuids():
            raise Exception("Not installed")
        enabled_uuids = self.enabled_uuids()
        if uuid not in enabled_uuids:
            return True
        enabled_uuids.remove(uuid)
        Gio.Settings("org.gnome.shell").set_value(
            "enabled-extensions",
            GLib.Variant("as", list(enabled_uuids)),
        )
        return True

    @staticmethod
    def install(uuid: str) -> Extension:
        ext = Extension(uuid)
        download_url = API_ROOT + ext.remote_meta["download_url"]
        dest_dir = os.path.join(EXTENSION_DIR, uuid)
        download_and_extract_zip(download_url, dest_dir)
        return ext

    def uninstall(self, uuid: str) -> None:
        self.disable(uuid)
        shutil.rmtree(os.path.join(EXTENSION_DIR, uuid))
