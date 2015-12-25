import urllib.parse
import urllib.request
import json
import subprocess

from io import BytesIO
from zipfile import ZipFile


def gnome_shell_version():
    """Get Gnome Shell version number.

    :returns: tuple(major, minor, patch)

    """
    cmd = subprocess.Popen(
            ['gnome-shell', '--version'],
            stdout=subprocess.PIPE
    )
    version_str = cmd.communicate()[0].split()[-1]
    return tuple(int(i) for i in version_str.split(b'.'))


GNOME_SHELL_VERSION = gnome_shell_version()


def get_json_response(endpoint, query):
    """Returns json response.

    :endpoint: url string
    :query: query dict
    :returns: response dict

    """
    query_string = urllib.parse.urlencode(query)
    full_url = "{}/?{}".format(endpoint, query_string)
    with urllib.request.urlopen(full_url) as f:
        data = f.read().decode('utf-8')
    return json.loads(data)


def download_and_extract_zip(url, dest):
    """Download zipfile and extract to destination dir.

    :url: url to download zipfile
    :dest: destination directory

    """
    with urllib.request.urlopen(url) as f:
        data = f.read()
    zipfile = ZipFile(BytesIO(data))
    zipfile.extractall(path=dest)


def reload_gnome_shell():
    """Reload gnome shell.

    """
    cmd = subprocess.Popen(
        "dbus-send --type=method_call --dest=org.gnome.Shell /org/gnome/Shell "
        "org.gnome.Shell.Eval string:'global.reexec_self()'",
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True
    )
    cmd.communicate()
