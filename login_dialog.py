import os

from qgis.core import Qgis
from qgis.PyQt.QtWidgets import QDialog, QWidget
from qgis.gui import QgisInterface
from .ui import UILoginDialog
from typing import Optional

class LoginDialog(QDialog, UILoginDialog):
    def __init__(self, iface: QgisInterface, parent: Optional[QWidget] = None):
        super(LoginDialog, self).__init__(parent)
        self.iface = iface
        self.setupUi(self)
        self.buttonBox.accepted.connect(self.on_login)
        self.buttonBox.rejected.connect(self.on_close)

    def on_login(self) -> None:
        self.iface.messageBar().pushMessage("Login", "Login button clicked", level=Qgis.Info)
    
    def on_close(self) -> None:
        self.close()