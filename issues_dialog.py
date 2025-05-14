from qgis.PyQt.QtCore import QAbstractTableModel, QSortFilterProxyModel, Qt
from qgis.PyQt.QtWidgets import QDialog, QWidget
from qgis.gui import QgisInterface
from .ui import UIIssuesDialog
from typing import Optional
from logic.fetch_queries import fetch_queries
from logic.fetch_issues import fetch_issues


class Model(QAbstractTableModel):
    def __init__(self, datalist: list, parent=None):
        QAbstractTableModel.__init__(self, parent)
        self.datalist = datalist
        # Define the headers from the datalist
        if datalist and isinstance(datalist[0], dict):
            self.headers = list(datalist[0].keys())

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


class IssuesDialog(QDialog, UIIssuesDialog):
    def __init__(self, iface: QgisInterface, parent: Optional[QWidget] = None):
        super(IssuesDialog, self).__init__(parent)
        self.iface = iface
        self.setupUi(self)
        self._init_gui()

    def _init_gui(self) -> None:
        self.fetchIssuesButton.clicked.connect(self.on_fetch_issues)
        self.allRadioButton.toggled.connect(self.allRadioButtonClicked)
        self.customQueryRadioButton.toggled.connect(self.customQueryRadioButtonClicked)
        self.limitLineEdit.setText("100")
        self.allRadioButton.setChecked(True)
        pass

    def set_api_key(self, api_key: str) -> None:
        self.api_key = api_key

    def set_base_url(self, base_url: str) -> None:
        self.base_url = base_url

    def set_project_id(self, project_id: int) -> None:
        self.project_id = project_id

    def setup_custom_ui(self) -> None:
        queries = fetch_queries(self.base_url, self.api_key, self.project_id)
        if queries is None:
            return
        self.customQueriesComboBox.clear()
        for query in queries:
            self.customQueriesComboBox.addItem(query["name"], userData=query["id"])
        self.customQueriesComboBox.setCurrentIndex(-1)
        self.customQueriesComboBox.setPlaceholderText("Select a custom query")

    def allRadioButtonClicked(self) -> None:
        self.customQueriesComboBox.setEnabled(False)

    def customQueryRadioButtonClicked(self) -> None:
        self.customQueriesComboBox.setEnabled(True)

    def on_fetch_issues(self) -> None:
        limit = int(self.limitLineEdit.text())
        if self.allRadioButton.isChecked():
            query_id = None
        else:
            query_id = self.customQueriesComboBox.currentData()
        issues = fetch_issues(
            self.base_url, self.api_key, self.project_id, limit, query_id
        )
        if issues is None:
            return
        self._set_issues(issues)

    def _set_issues(self, issues: list) -> None:
        model = Model(issues)
        proxy_model = QSortFilterProxyModel()
        proxy_model.setDynamicSortFilter(True)
        proxy_model.setSourceModel(model)
        proxy_model.setSortCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.issuesTableView.setModel(proxy_model)
        self.issuesTableView.resizeColumnsToContents()
        self.issuesTableView.resizeRowsToContents()
        self.issuesTableView.setSortingEnabled(True)
        self.issuesTableView.sortByColumn(0, Qt.SortOrder.AscendingOrder)
        self.issuesTableView.resizeRowsToContents()
        self.issuesTableView.setSelectionBehavior(
            self.issuesTableView.SelectionBehavior.SelectRows
        )
        self.issuesTableView.setSelectionMode(
            self.issuesTableView.SelectionMode.MultipleSelection
        )
