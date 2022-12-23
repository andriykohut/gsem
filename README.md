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

### Updating the package

Run `pip install -U --user gsem` for user installation or `sudo pip install -U gsem` for global installation.

## Features:
* list installed
* list enabled/disabled
* list outdated
* extension info
* search
* enable/disable
* install/uninstall/reinstall
* update

## Contributing

Development on latest python version is preferred, as of now it's 3.9.
To start you'll need the following setup:

Example uses pyenv to install latest python and manage virtualenv. Run the following commands from the root of the repository.

```sh
pyenv install 3.9.2           # install latest python version
pyenv virtualenv 3.9.2 gsem   # create gsem virtual environment
pyenv activate gsem           # activate the venv
pyenv local gsem              # set local python version for the repo
poetry install                # install all dependencies inside the virtual environment
pre-commit install            # install pre-commit hooks
```

Run all the linters:
```sh
pre-commit run -a
```

## TODO:
* pin
