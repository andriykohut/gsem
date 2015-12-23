import urllib.parse
import urllib.request
import json
import subprocess


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
