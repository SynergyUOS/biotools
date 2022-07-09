import importlib.resources
from os import PathLike
from pathlib import Path
from typing import Sequence, Union

import arcpy
import arcpy.management as am
import pandas as pd


def _init_projection(name):
    with importlib.resources.path("biotools.res", name) as path:
        return arcpy.SpatialReference(path)


def _init_biotope_codes():
    with importlib.resources.path("biotools.res", "biotope_codes.csv") as path:
        df = pd.read_csv(path)

    result = {}
    for large_category_code, sub_df in df.groupby("LARGE_CATEGORY_CODE"):
        result[large_category_code] = sub_df["MEDIUM_CATEGORY_CODE"].tolist()
    return result


WGS1984_PRJ = _init_projection("GCS_WGS_1984.prj")
ITRF2000_PRJ = _init_projection("ITRF_2000_UTM_K.prj")

BIOTOPE_CODES = _init_biotope_codes()


def get_medium_codes(large_codes):
    result = []
    for large_code in large_codes:
        result += BIOTOPE_CODES[large_code]
    return result


def query_isin(field, targets):
    return " OR ".join([f"{field} = '{target}'" for target in targets])


def get_fields(layer):
    return [field.name for field in arcpy.ListFields(str(layer))]


def shp_to_df(shp: Union[str, PathLike]):
    shp = str(shp)
    fields = get_fields(shp)
    table = [row for row in arcpy.da.SearchCursor(shp, fields)]
    result_df = pd.DataFrame(table, columns=fields)
    result_df = result_df.set_index(fields[0])
    return result_df


def get_coordsys(layer):
    """for debug"""
    return arcpy.Describe(layer).spatialReference.name


def clean_join(target_shp, df, result_shp, on="BT_ID"):
    target_shp = str(target_shp)
    result_shp = str(result_shp)
    temp_csv = str(Path(result_shp).with_suffix(".csv"))
    df.to_csv(temp_csv, encoding="euc-kr", index=False)

    joined = am.AddJoin(target_shp, on, temp_csv, on)
    if Path(result_shp).exists():
        am.Delete(result_shp)
    am.CopyFeatures(joined, result_shp)

    fields = arcpy.ListFields(result_shp)
    good_names = get_fields(target_shp) + df.columns.tolist()
    for field, good_name in zip(fields, good_names):
        if field.type == "OID" or field.type == "Geometry":
            continue
        if good_name not in get_fields(result_shp):     # skip double "BT_ID"
            am.AddField(result_shp, good_name, field.type)
            am.CalculateField(result_shp, good_name, f"!{field.name}!")
        am.DeleteField(result_shp, field.name)

    return result_shp


def any_raster(rasters: Sequence[arcpy.Raster]):
    """For each cell, get the probability that at least one probability will be true.
    """
    complements = [1.0 - raster for raster in rasters]
    product = complements[0]
    for complement in complements[1:]:
        product *= complement
    return 1.0 - product
