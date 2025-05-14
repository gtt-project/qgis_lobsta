import os
from qgis.core import Qgis
from qgis.PyQt.QtCore import QCoreApplication, QSettings, QTranslator
from qgis.gui import QgisInterface
from qgis.PyQt.QtWidgets import QAction
from .login_dialog import LoginDialog
from .project_dialog import ProjectDialog
from .issues_dialog import IssuesDialog
from .ui import IconLobsta
from typing import List, Optional
from logic.key_management import fetch_auth_config, delete_auth_config


class Lobsta:
    """QGIS lobsta plugin main class."""

    def __init__(self, iface: QgisInterface):
        self.iface = iface

        self.plugin_dir = os.path.dirname(__file__)

        locale = QSettings().value("locale/userLocale")[0:2]
        locale_path = os.path.join(self.plugin_dir, "i18n", f"lobsta_{locale}.qm")
        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # declare instance attributes
        self.actions: List[QAction] = []  # type: ignore
        self.menu = "Lobsta"

        self.toolbar = self.iface.addToolBar("Lobsta")
        self.toolbar.setObjectName("Lobsta")

        self.login_dialog: Optional[LoginDialog] = None
        self.project_dialog: Optional[ProjectDialog] = None
        self.issues_dialog: Optional[IssuesDialog] = None
        self.api_key: Optional[str] = None
        self.base_url: Optional[str] = None

    def tr(self, message: str) -> str:
        return QCoreApplication.translate("Lobsta", message)

    def initGui(self) -> None:
        self.setupLoginAction()

    def setupLoginAction(self) -> None:
        self.clearActions()
        action = QAction(IconLobsta, self.tr("Login"), self.iface.mainWindow())
        action.triggered.connect(self.check_login)
        self.iface.addToolBarIcon(action)
        self.iface.addPluginToMenu(self.tr("&Lobsta"), action)
        self.actions.append(action)

    def addProjectAction(self) -> None:
        action = QAction(IconLobsta, self.tr("Projects"), self.iface.mainWindow())
        action.triggered.connect(self.on_projects)
        self.iface.addToolBarIcon(action)
        self.iface.addPluginToMenu(self.tr("&Lobsta"), action)
        self.actions.append(action)

    def addLogoffAction(self) -> None:
        action = QAction(IconLobsta, self.tr("Logoff"), self.iface.mainWindow())
        action.triggered.connect(self.on_logoff)
        self.iface.addPluginToMenu(self.tr("&Lobsta"), action)
        self.actions.append(action)

    def check_login(self) -> None:
        """Check if the user is logged in."""
        auth_config = fetch_auth_config()
        if auth_config:
            self.base_url = auth_config["url"]
        else:
            self.base_url = None
        if auth_config and auth_config["api_key"]:
            self.iface.messageBar().pushMessage(
                self.tr("Login"), self.tr("User is logged in"), level=Qgis.Success
            )
            self.api_key = auth_config["api_key"]
            self.clearActions()
            self.addProjectAction()
            self.addLogoffAction()
        else:
            self.api_key = None
            self.on_login()

    def on_login(self) -> None:
        if not self.login_dialog:
            self.login_dialog = LoginDialog(self.iface)
        self.login_dialog.show()
        if self.base_url:
            self.login_dialog.set_url(self.base_url)
        self.login_dialog.set_after_login(self.check_login)

    def on_projects(self) -> None:
        if not self.project_dialog:
            self.project_dialog = ProjectDialog(self.iface)
        if self.api_key:
            self.project_dialog.set_api_key(self.api_key)
        if self.base_url:
            self.project_dialog.set_base_url(self.base_url)
        self.project_dialog.show()
        self.project_dialog.set_open_issues_dialog(self.on_issues)
        self.issues_dialog = None

    def on_issues(self, project_id: int) -> None:
        """Open the issues dialog."""
        if not self.issues_dialog:
            self.issues_dialog = IssuesDialog(self.iface)
        if self.api_key:
            self.issues_dialog.set_api_key(self.api_key)
        if self.base_url:
            self.issues_dialog.set_base_url(self.base_url)
        self.issues_dialog.set_project_id(project_id)
        self.issues_dialog.setup_custom_ui()
        self.issues_dialog.show()

    def on_logoff(self) -> None:
        """Log off the user."""
        delete_auth_config()
        self.iface.messageBar().pushMessage(
            self.tr("Logoff"), self.tr("User logged off"), level=Qgis.Success
        )
        self.api_key = None
        self.project_dialog = None
        self.issues_dialog = None
        self.setupLoginAction()

    def unload(self) -> None:
        self.clearActions()

    def clearActions(self) -> None:
        """Clear all actions from the toolbar."""
        for action in self.actions:
            self.iface.removePluginMenu(self.menu, action)
            self.iface.removeToolBarIcon(action)
        self.actions = []
