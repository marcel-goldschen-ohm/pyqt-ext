# pyqt-ext
Collection of PyQt/PySide widgets/tools.

![GitHub Tag](https://img.shields.io/github/v/tag/marcel-goldschen-ohm/pyqt-ext?cacheSeconds=1)
![build-test](https://github.com/marcel-goldschen-ohm/pyqt-ext/actions/workflows/build-test.yml/badge.svg)
![GitHub Release](https://img.shields.io/github/v/release/marcel-goldschen-ohm/pyqt-ext?include_prereleases&cacheSeconds=1)
![publish](https://github.com/marcel-goldschen-ohm/pyqt-ext/actions/workflows/publish.yml/badge.svg)

The goal of this repo is to provide useful extensions to PyQt all in one place. There are several other PyQt extensions out there, but to my knowledge all of these are very limited in scope. Given this goal, **I encourage everyone to contribute your own extensions to this repo!**

In addition to being useful out-of-the-box, you may find these tools to be helpful templates for rolling your own custom widgets.

- [Install](#install)
- [Documentation](#documentation)

## Install
Requires a PyQt package. Should work with PySide6, PyQt6, or PyQt5.
```shell
pip install PySide6
```
Install latest release version:
```shell
pip install pyqt-ext
```
Or install latest development version:
```shell
pip install pyqt-ext@git+https://github.com/marcel-goldschen-ohm/pyqt-ext
```

## Documentation
:construction:

- `graph/`
    - Graph style utils
- `tree/`
    - [Abstract tree model/view interface](docs/AbstractTree.md) - *Because who wants to go through the pain of deciphering Qt's convoluted tree model/view design which is infuriating each and every time you work with it.*
    - [(key, value) tree model/view](docs/KeyValueTree.md) - *An exampel of how easy it is to build custom tree behavior using the abstract interface above.*
- `utils/`
    - [Color utils](docs/ColorUtils.md)
- `widgets/`
    - Collapsible section
    - [Color selection button](docs/ColorButton.md)
    - [Multi-value spinbox](docs/MultiValueSpinBox.md)
    - Table widget with copy/paste
