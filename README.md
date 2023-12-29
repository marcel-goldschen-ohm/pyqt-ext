# PyQt-tools
Collection of PyQt/PySide widgets/tools.

Some of these may just be useful as templates for rolling your own custom tool.

- [PyQtAbstractTreeItem](#pyqtabstracttreeitem)
- [PyQtAbstractTreeModel](#pyqtabstracttreemodel)
- [PyQtAbstractTreeView](#pyqtabstracttreeview)
- [PyQtColorButton](#pyqtcolorbutton)
- [PyQtKeyValueTreeItem](#pyqtkeyvaluetreeitem)
- [PyQtKeyValueTreeModel](#pyqtkeyvaluetreemodel)
- [PyQtKeyValueTreeView](#pyqtkeyvaluetreeview)
- [PyQtMultiValueSpinBox](#pyqtmultivaluespinbox)
- [PyQtXYDataStyle](#pyqtxydatastyle)

# Install
Typically you would just include these files in your project as desired, or fork this repo and add it to your project repo as a submodule.

However, you can also install it locally with [pdm]():
```shell
# clone repo and navigate to local repo
git clone https://github.com/marcel-goldschen-ohm/PyQt-tools.git
cd PyQt-tools

# install pipx
pip install pipx
pipx ensure path

# install pdm
pipx install pdm

# tell pdm to use the python interpreter associated with your desired environment
# e.g., conda activate env-my-project
pdm use /path/to/your/env/python

# install pyqt-tools for local development
pdm install
```
