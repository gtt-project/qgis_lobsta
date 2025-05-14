from qgis.core import Qgis
from qgis.PyQt.QtCore import QAbstractTableModel, QSortFilterProxyModel, Qt
from qgis.PyQt.QtWidgets import QDialog, QWidget
from qgis.gui import QgisInterface
from .ui import UIProjectDialog
from typing import Optional, Callable
from logic.fetch_projects import fetch_projects

HEADERS = (
    "id",
    "name",
    "description",
)


class Model(QAbstractTableModel):
    def __init__(self, datalist: list, parent=None):
        QAbstractTableModel.__init__(self, parent)
        self.datalist = datalist
        self.headers = HEADERS

    def rowCount(self, parent=None):
        return len(self.datalist)

    def columnCount(self, parent=None):
        return len(self.headers)

    def flag(self, index):
        return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable

    def data(self, index, role):
        if role == Qt.ItemDataRole.DisplayRole:
            row = index.row()
            column = index.column()
            key = self.headers[column]
            return self.datalist[row][key]

    def headerData(self, section, orientation, role):
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                if section < len(self.headers):
                    return self.headers[section]
                else:
                    return "not implemented"
            else:
                return section + 1


class ProjectDialog(QDialog, UIProjectDialog):
    def __init__(self, iface: QgisInterface, parent: Optional[QWidget] = None):
        super(ProjectDialog, self).__init__(parent)
        self.iface = iface
        self.setupUi(self)
        self._init_gui()

    def _init_gui(self) -> None:
        self._set_projects([])
        self.fetchProjectsButton.clicked.connect(self.on_fetch_projects)
        self.openProjectButton.clicked.connect(self.on_click_project)

    def _set_projects(self, projects: list) -> None:
        model = Model(projects)
        proxy_model = QSortFilterProxyModel()
        proxy_model.setDynamicSortFilter(True)
        proxy_model.setSourceModel(model)
        proxy_model.setSortCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.projectTableView.setModel(proxy_model)
        self.projectTableView.setCornerButtonEnabled(True)
        self.projectTableView.setSortingEnabled(True)
        self.projectTableView.sortByColumn(0, Qt.SortOrder.AscendingOrder)
        self.projectTableView.resizeColumnsToContents()
        self.projectTableView.resizeRowsToContents()
        self.projectTableView.setSelectionBehavior(
            self.projectTableView.SelectionBehavior.SelectRows
        )
        self.projectTableView.setSelectionMode(
            self.projectTableView.SelectionMode.SingleSelection
        )

    def get_selected_project(self) -> Optional[int]:
        selection_rows = self.projectTableView.selectionModel().selectedRows()
        for row in selection_rows:
            project_data = self.projectTableView.model().index(row.row(), 0).data()
            print(project_data)
            return int(project_data)
        return None

    def set_api_key(self, api_key: str) -> None:
        self.api_key = api_key

    def set_base_url(self, base_url: str) -> None:
        self.base_url = base_url

    def set_open_issues_dialog(self, callable: Callable) -> None:
        self.open_issues_dialog_callable = callable

    def on_fetch_projects(self) -> None:
        if self.api_key and self.base_url:
            projects = fetch_projects(self.base_url, self.api_key)
            if projects:
                self._set_projects(projects)
            else:
                self.iface.messageBar().pushMessage(
                    self.tr("Projects"),
                    self.tr("No projects found or error fetching projects."),
                    level=Qgis.Critical,
                )
        else:
            self.iface.messageBar().pushMessage(
                self.tr("Projects"),
                self.tr("API key or base URL not set."),
                level=Qgis.Critical,
            )

    def on_click_project(self) -> None:
        project_id = self.get_selected_project()
        if project_id:
            self.close()
            self.open_issues_dialog_callable(project_id)
        else:
            self.iface.messageBar().pushMessage(
                self.tr("Projects"),
                self.tr("No project selected."),
                level=Qgis.Critical,
            )
