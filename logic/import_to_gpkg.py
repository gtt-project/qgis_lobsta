from qgis.core import (
    QgsVectorFileWriter,
    QgsVectorLayer,
    QgsProject,
    QgsWkbTypes,
)
from collections import defaultdict
import os


def import_to_gpkg(geojson_paths: list[str], gpkg_path: str) -> None:
    """
    Import GeoJSON files to a GeoPackage.

    Args:
        geojson_paths (list[str]): List of paths to GeoJSON files.
        gpkg_path (str): Path to the output GeoPackage file.
    """
    # Create a dictionary to hold layers by their names
    type_feature_map = defaultdict(list)
    fields_map = {}

    for geojson_path in geojson_paths:
        # Load the GeoJSON file as a QgsVectorLayer
        layer = QgsVectorLayer(geojson_path, os.path.basename(geojson_path), "ogr")
        if not layer.isValid():
            print(f"Failed to load layer from {geojson_path}")
            continue

        for feat in layer.getFeatures():
            geom = feat.geometry()
            geom_type = QgsWkbTypes.displayString(geom.wkbType())
            type_feature_map[geom_type].append(feat)

            if geom_type not in fields_map:
                fields_map[geom_type] = layer.fields()

    # Create the GeoPackage
    for geom_type, features in type_feature_map.items():
        crs = (
            features[0].geometry().crs()
            if hasattr(features[0].geometry(), "crs")
            else layer.crs()
        )
        temp_layer = QgsVectorLayer(
            f"{geom_type}?crs={crs.authid()}", geom_type, "memory"
        )
        temp_layer.dataProvider().addAttributes(fields_map[geom_type])
        temp_layer.updateFields()

        temp_layer.dataProvider().addFeatures(features)

        # Save the layer to the GeoPackage
        options = QgsVectorFileWriter.SaveVectorOptions()
        options.driverName = "GPKG"
        options.layerName = geom_type
        if not os.path.exists(gpkg_path):
            options.actionOnExistingFile = QgsVectorFileWriter.CreateOrOverwriteFile
        else:
            options.actionOnExistingFile = QgsVectorFileWriter.CreateOrOverwriteLayer

        error, _, _, _ = QgsVectorFileWriter.writeAsVectorFormatV3(
            temp_layer,
            gpkg_path,
            QgsProject.instance().transformContext(),
            options,
        )

        if error != QgsVectorFileWriter.NoError:
            print(f"Failed to write layer {geom_type} to GeoPackage: {error}")
