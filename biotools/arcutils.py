import io
from os import PathLike
import pathlib
import pkgutil

import arcpy
import pandas as pd


def _init_biotope_codes():
    raw_data = pkgutil.get_data(__name__, "res/biotope_codes.csv")
    df = pd.read_csv(io.StringIO(raw_data.decode()))

    result = {}
    for large_category_code, sub_df in df.groupby("LARGE_CATEGORY_CODE"):
        result[large_category_code] = sub_df["MEDIUM_CATEGORY_CODE"].tolist()
    return result


BIOTOPE_CODES = _init_biotope_codes()


def _init_projection(path):
    raw_data = pkgutil.get_data(__name__, path)
    return arcpy.SpatialReference(text=raw_data.decode())


WGS1984_PRJ = _init_projection("res/GCS_WGS_1984.prj")
ITRF2000_PRJ = _init_projection("res/ITRF_2000_UTM_K.prj")


def get_biotope_codes(large_codes):
    result = []
    for large_code in large_codes:
        result += BIOTOPE_CODES[large_code]
    return result


def get_fields(layer):
    return [field.name for field in arcpy.ListFields(str(layer))]


def get_oid_field(layer):
    return arcpy.ListFields(layer, field_type="OID")[0].name


def layer_to_df(layer: PathLike):
    layer = str(layer)
    fields = get_fields(layer)
    table = [row for row in arcpy.da.SearchCursor(layer, fields)]
    result_df = pd.DataFrame(table, columns=fields)
    result_df = result_df.set_index(fields[0])
    return result_df


def make_isin_query(field, large_category_codes):
    medium_category_codes = []
    for large_category_code in large_category_codes:
        medium_category_codes += BIOTOPE_CODES[large_category_code]
    return " OR ".join([f"{field} = '{code}'" for code in medium_category_codes])


def get_cs(layer):
    """for debug"""
    return arcpy.Describe(layer).spatialReference.name


def fix_fid(layer):
    """Create BT_ID field to `biotope_layer` permanently."""
    if "BT_ID" not in get_fields(layer):
        result = arcpy.management.CalculateField(
            layer,
            "BT_ID",
            f"'BT_ID_!FID!'",
            expression_type="PYTHON3",
            field_type="TEXT"
        )
    return


def load_asc(path, prj):
    """Deletion is required.
    ```
    raster = arcutils.load_asc(path, prj)
    # some processes...
    arcpy.management.Delete(raster)
    ```
    """
    temp_name = f"memory/{pathlib.Path(path).stem}"
    result = arcpy.management.CopyRaster(path, temp_name)
    arcpy.management.DefineProjection(result, prj)
    return result
