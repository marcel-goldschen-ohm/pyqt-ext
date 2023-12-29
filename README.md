# PyQt-tools
Collection of PyQt/PySide widgets/tools.

Some of these may just be useful as templates for rolling your own custom tool.

- [PyQtAbstractTreeItem](docs/PyQtAbstractTreeItem.md)
- [PyQtAbstractTreeModel](docs/PyQtAbstractTreeModel.md)
- [PyQtAbstractTreeView](docs/PyQtAbstractTreeView.md)
- [PyQtColorButton](docs/PyQtColorButton.md)
- [PyQtKeyValueTreeItem](docs/PyQtKeyValueTreeItem.md)
- [PyQtKeyValueTreeModel](docs/PyQtKeyValueTreeModel.md)
- [PyQtKeyValueTreeView](docs/PyQtKeyValueTreeView.md)
- [PyQtMultiValueSpinBox](docs/PyQtMultiValueSpinBox.md)
- [PyQtXYDataStyle](docs/PyQtXYDataStyle.md)

# Install
Typically you would just include these files in your project as desired, or fork this repo and add it to your project repo as a submodule.

Although the package structure is ready for deployment on PyPI, I don't think it is worthy of being its own package yet. However, you can install it locally with [pdm]().

Install pdm:
```shell
pip install pipx
pipx ensurepath
pipx install pdm
```

Install pyqt-tools for desired python interpreter
```shell
git clone https://github.com/marcel-goldschen-ohm/PyQt-tools.git
cd PyQt-tools
pdm use /path/to/your/env/python
pdm install
```
