from pathlib import Path

from qgis.PyQt import uic
from qgis.PyQt.QtGui import QIcon

cwd = Path(__file__).parent
icon_path = cwd / "icon.png"
IconLobsta = QIcon(str(icon_path))
UILoginDialog, _ = uic.loadUiType(str(cwd / "login_dialog.ui"))