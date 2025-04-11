from qgis.core import Qgis
from qgis.PyQt.QtWidgets import QDialog, QWidget
from qgis.gui import QgisInterface
from .ui import UILoginDialog
from logic.authenticate import authenticate, authenticate_via_api, User
from logic.key_management import store_auth_config
from typing import Optional, Callable


class LoginDialog(QDialog, UILoginDialog):
    def __init__(self, iface: QgisInterface, parent: Optional[QWidget] = None):
        super(LoginDialog, self).__init__(parent)
        self.iface = iface
        self.setupUi(self)
        self.buttonBox.accepted.connect(self.on_login)
        self.buttonBox.rejected.connect(self.on_close)

    def on_login(self) -> None:
        url = self.lobsta_url_field.text()
        username = self.lobsta_user_name_field.text()
        password = self.lobsta_password_field.text()
        api_key = self.lobsta_api_key_field.text()
        if len(api_key) > 0:
            response = authenticate_via_api(url, api_key)
        else:
            response = authenticate(url, username, password)
        if isinstance(response, dict) and all(key in response for key in User.__annotations__.keys()):
            self.iface.messageBar().pushMessage(self.tr("Login"), self.tr("Login successful"), level=Qgis.Success)
            new_api_key = response["user"]["api_key"]
            store_auth_config(url, username, password, new_api_key)
            if self.after_login:
                self.after_login()
            self.close()
        else:
            self.iface.messageBar().pushMessage(self.tr("Login"), self.tr("Login failed"), level=Qgis.Critical)
    
    def on_close(self) -> None:
        self.close()

    def set_url(self, url: str) -> None:
        self.lobsta_url_field.setText(url)

    def set_after_login(self, after_login: Callable) -> None:
        self.after_login = after_login