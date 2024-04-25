""" PySide/PyQt button for selecting and displaying a color.
"""

from qtpy.QtGui import QColor


ColorType = str | tuple[int | float] | list[int | float] | QColor | None


def toQColor(color: ColorType, name_map: dict[str, ColorType] = None) -> QColor:
    if color is None:
        return QColor('transparent')
    if isinstance(color, QColor):
        return color
    if isinstance(color, str):
        color = color.strip()
        if (name_map is not None) and (color in name_map):
            return toQColor(name_map[color])
        elif QColor.isValidColorName(color):
            return QColor(color)
        else:
            # (r,g,b) or (r,g,b,a)
            color = color.lstrip('(').rstrip(')').split(',')
            try:
                color = [int(part) for part in color]
            except:
                color = [float(part) for part in color]
    # (r,g,b) or (r,g,b,a)
    if isinstance(color[0], int):
        return QColor(*color)
    elif isinstance(color[0], float):
        return QColor.fromRgbF(*color)


def toColorStr(color: ColorType) -> str:
    if color is None:
        return None
    if isinstance(color, QColor):
        # (r,g,b,a) in [0,255]
        return f'({color.red()}, {color.green()}, {color.blue()}, {color.alpha()})'
    if isinstance(color, str):
        if ',' in color:
            # (r,g,b) or (r,g,b,a)
            return toColorStr(toQColor(color))
        # assume color str is valid 
        return color
    if isinstance(color, tuple) or isinstance(color, list):
        # (r,g,b) or (r,g,b,a)
        return '(' + ', '.join([str(part) for part in color]) + ')'