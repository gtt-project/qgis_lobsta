import sys
from qgis.gui import QgisInterface
from qgis.PyQt.QtWidgets import QAction
from .login_dialog import LoginDialog
from .ui import IconLobsta
from typing import List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    # This is a workaround of Pylance
    try:
        from PyQt6.QtWidgets import QAction as QActionType # type: ignore
    except ImportError:
        from PyQt5.QtWidgets import QAction as QActionType

class Lobsta:
    """QGIS lobsta plugin main class."""

    def __init__(self, iface: QgisInterface):
        self.iface = iface

        # declare instance attributes
        self.actions: List[QActionType] = []
        self.menu = "Lobsta"

        self.toolbar = self.iface.addToolBar("Lobsta")
        self.toolbar.setObjectName("Lobsta")

        self.dialog: Optional[LoginDialog] = None
    
    def initGui(self) -> None:
        action = QAction(IconLobsta, "Login", self.iface.mainWindow())
        action.triggered.connect(self.on_login)
        self.iface.addToolBarIcon(action)
        self.iface.addPluginToMenu("&Lobsta", action)
        self.actions.append(action)

    def on_login(self) -> None:
        if not self.dialog:
            self.dialog = LoginDialog(self.iface)
        self.dialog.show()

    def unload(self) -> None:
        for action in self.actions:
            self.iface.removePluginMenu(self.menu, action)
            self.iface.removeToolBarIcon(action)