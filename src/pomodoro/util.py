# SPDX-License-Identifier: GPL-3.0-or-later (see AUTHORS file)

from PyQt5.QtCore import QFileInfo
from PyQt5.QtGui import QIcon

def makeIcon(name, end="png"):
    iconPath = QFileInfo(__file__).dir()
    iconPath.cdUp()
    iconPath.cd("icons")
    iconPath = iconPath.filePath(f"{name}.{end}")
    return QIcon(iconPath)