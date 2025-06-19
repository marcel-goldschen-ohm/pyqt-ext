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
Requires a PyQt package. Should work with PySide6, PyQt6, or PyQt5. *Note: pyqtgraph is incompatible with PySide6=6.9.1, not sure why?*
```shell
pip install "PySide6<6.9.1"
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

- `tree/`
    - **[Abstract tree model/view interface](docs/AbstractTree.md)** [[code](src/pyqt_ext/tree/)] [[example](examples/CustomTreeExample.py)]: Because who wants to go through the pain of deciphering Qt's convoluted tree model/view design which is infuriating each and every time you work with it. Includes drag-n-drop moving within a tree. See [example](examples/CustomTreeExample.py) for a custom tree using this interface.
    - **[(Key, Value) tree model/view](docs/KeyValueTree.md)** [[code](src/pyqt_ext/tree/)] [[example](examples/KeyValueTreeExample.py)]: Tree model/view for (key, value) pairs in a dict or list (keys are list indices). Can be nested to any level. Uses the abstract tree interface above.
- `utils/`
    - **Color** [[code](src/pyqt_ext/utils/Color.py)]: QColor conversions.
- `widgets/`
    - **Collapsible section** [[code](src/pyqt_ext/widgets/CollapsibleSection.py)] [[example](examples/CollapsibleSectionExample.py)]: Widget with header that can be toggled to expand/collapse a layout.
    - **Color selection button** [[code](src/pyqt_ext/widgets/ColorButton.py)] [[example](examples/ColorButtonExample.py)]: Tool button that displays selected color and opens color selection dialog on click.
    - **Multi-value spinbox** [[code](src/pyqt_ext/widgets/MultiValueSpinBox.py)] [[example](examples/MultiValueSpinBoxExample.py)]: Spin box allowing multiple selected values and value ranges. Works with string values too.
    - **Table widget with copy/paste** [[code](src/pyqt_ext/widgets/TableWidgetWithCopyPaste.py)]: QTableWidget with copy/paste to/from clipboard.
