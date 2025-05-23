from qgis.core import Qgis
from qgis.PyQt.QtCore import QAbstractTableModel, QSortFilterProxyModel, Qt
from qgis.PyQt.QtWidgets import QDialog, QWidget
from qgis.gui import QgisInterface, QgsFileWidget
from .ui import UIIssuesDialog
from typing import Optional
from logic.fetch_queries import fetch_queries
from logic.fetch_issues import fetch_issues
from logic.fetch_geojsons import fetch_geojsons
from logic.import_to_gpkg import import_to_gpkg
import tempfile
import os


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
        self.file_path: Optional[str] = None

    def _init_gui(self) -> None:
        self.fetchIssuesButton.clicked.connect(self.on_fetch_issues)
        self.allRadioButton.toggled.connect(self.allRadioButtonClicked)
        self.customQueryRadioButton.toggled.connect(self.customQueryRadioButtonClicked)
        self.limitLineEdit.setText("100")
        self.allRadioButton.setChecked(True)
        self.exportQgsFileWidget.fileChanged.connect(self.on_export_file_changed)
        self.exportQgsFileWidget.setFilter("GeoPackage files (*.gpkg);;All files (*)")
        self.exportQgsFileWidget.setStorageMode(QgsFileWidget.SaveFile)
        self.exportButton.setEnabled(False)
        self.exportButton.clicked.connect(self.on_export_button_clicked)
        self.exportAllRadioButton.setChecked(True)
        self.exportProgressBar.setValue(0)

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

    def on_export_file_changed(self, file_path: str) -> None:
        if file_path:
            self.exportButton.setEnabled(True)
            self.file_path = file_path
        else:
            self.exportButton.setEnabled(False)
            self.file_path = None

    def on_export_button_clicked(self) -> None:
        if self.file_path is None:
            return
        if os.path.exists(self.file_path):
            self.iface.messageBar().pushMessage(
                self.tr("Export"),
                self.tr("File already exists. Please choose a different file."),
                level=Qgis.Critical,
            )
            return
        # list of all issues or selected issues
        if self.exportAllRadioButton.isChecked():
            model = self.issuesTableView.model()
            selected_indexes = []
            for row in range(model.rowCount()):
                for column in range(model.columnCount()):
                    index = model.index(row, column)
                    if model.data(index) is not None:
                        selected_indexes.append(index)
        else:
            selected_indexes = self.issuesTableView.selectedIndexes()
        selected_issues = []
        for index in selected_indexes:
            if index.column() == 0:
                selected_issues.append(self.issuesTableView.model().data(index))
        if len(selected_issues) == 0:
            self.iface.messageBar().pushMessage(
                self.tr("Export"), self.tr("No issues selected"), level=Qgis.Critical
            )
            return
        # Export the selected issues to the specified file
        # Create a temporary directory to store the geojson files
        temp_dir = tempfile.TemporaryDirectory()
        geojson_paths = fetch_geojsons(
            temp_dir, self.base_url, self.api_key, selected_issues
        )
        self.exportProgressBar.setValue(50)
        if len(geojson_paths) == 0:
            self.iface.messageBar().pushMessage(
                self.tr("Export"),
                self.tr("No geojsons found for the selected issues"),
                level=Qgis.Critical,
            )
            self.exportProgressBar.setValue(0)
            return
        # Import the geojsons to the specified file
        import_to_gpkg(geojson_paths, self.file_path)
        self.exportProgressBar.setValue(100)
        # Clean up the temporary directory
        temp_dir.cleanup()
        self.iface.messageBar().pushMessage(
            self.tr("Export"),
            self.tr("Export successful"),
            level=Qgis.Success,
        )
        # TODO: Open the exported file in QGIS

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
            self.issuesTableView.SelectionMode.MultiSelection
        )
