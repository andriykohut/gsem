# gsem

[![PyPI version](https://badge.fury.io/py/gsem.svg)](https://pypi.org/project/gsem/)

*gsem* - Command line extension manager for Gnome-Shell

```
usage: gsem [-h]
            {ls,enabled,disabled,outdated,info,install,reinstall,uninstall,update,search,enable,disable}
            ...

Gnome-Shell extension manager

positional arguments:
  {ls,enabled,disabled,outdated,info,install,reinstall,uninstall,update,search,enable,disable}
    ls                  list installed extensions
    enabled             list enabled extensions
    disabled            list disabled extensions
    outdated            list outdated extensions
    info                show extension information
    install             install extension
    reinstall           reinstall extension
    uninstall           uninstall extension
    update              update extensions
    search              search extensions
    enable              enable extension
    disable             disable extension

optional arguments:
  -h, --help            show this help message and exit
```

## Installation

### User installation (recommended)
Run `pip install --user gsem`

Make sure you have `"$HOME/.local/bin"` in your `$PATH`.

### Global installation
Run `sudo pip install gsem`

## DONE:
* list installed
* list enabled/disabled
* list outdated
* extension info
* search
* enable/disable
* install/uninstall/reinstall
* update

## TODO:
* pin
