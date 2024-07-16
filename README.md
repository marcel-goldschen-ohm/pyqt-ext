# pyqt-ext
Collection of PyQt/PySide widgets/tools.

![GitHub Tag](https://img.shields.io/github/v/tag/marcel-goldschen-ohm/pyqt-ext)
![tests](https://github.com/marcel-goldschen-ohm/pyqt-ext/actions/workflows/build-test.yml/badge.svg)

![GitHub Release](https://img.shields.io/github/v/release/marcel-goldschen-ohm/pyqt-ext)

In addition to being useful out-of-the-box, you may find these tools to be helpful templates for rolling your own custom widgets.

- `graph/`
    - Graph style utils
- `tree/`
    - [Tree model/view interface](docs/AbstractTree.md)
    - [(key, value) tree model/view](docs/KeyValueTree.md)
- `utils/`
    - [Color utils](docs/ColorUtils.md)
- `widgets/`
    - Collapsible section
    - [Color selection button](docs/ColorButton.md)
    - [Multi-value spinbox](docs/MultiValueSpinBox.md)

# Install
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