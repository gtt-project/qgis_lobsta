from qgis.core import Qgis
from qgis.gui import QgisInterface
from qgis.PyQt.QtWidgets import QAction
from .login_dialog import LoginDialog
from .ui import IconLobsta
from typing import List, Optional
from logic.key_management import fetch_auth_config

class Lobsta:
    """QGIS lobsta plugin main class."""

    def __init__(self, iface: QgisInterface):
        self.iface = iface

        # declare instance attributes
        self.actions: List[QAction] = [] # type: ignore
        self.menu = "Lobsta"

        self.toolbar = self.iface.addToolBar("Lobsta")
        self.toolbar.setObjectName("Lobsta")

        self.login_dialog: Optional[LoginDialog] = None
    
    def initGui(self) -> None:
        action = QAction(IconLobsta, "Login", self.iface.mainWindow())
        action.triggered.connect(self.check_login)
        self.iface.addToolBarIcon(action)
        self.iface.addPluginToMenu("&Lobsta", action)
        self.actions.append(action)

    def check_login(self) -> None:
        """Check if the user is logged in."""
        auth_config = fetch_auth_config()
        if auth_config:
            self.base_url = auth_config["url"]
        else:
            self.base_url = None
        if auth_config and auth_config["api_key"]:
            self.iface.messageBar().pushMessage("Login", "User is logged in", level=Qgis.Success)
            self.api_key = auth_config["api_key"]
        else:
            self.api_key = None
            self.on_login()

    def on_login(self) -> None:
        if not self.login_dialog:
            self.login_dialog = LoginDialog(self.iface)
        self.login_dialog.show()
        if self.base_url:
            self.login_dialog.set_url(self.base_url)

    def unload(self) -> None:
        for action in self.actions:
            self.iface.removePluginMenu(self.menu, action)
            self.iface.removeToolBarIcon(action)