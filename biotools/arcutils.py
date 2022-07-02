import arcpy
import pandas as pd


def get_fields(layer):
    return [field.name for field in arcpy.ListFields(layer)]


def get_oid_field(layer):
    return arcpy.ListFields(layer, field_type="OID")[0].name


def layer_to_df(layer):
    fields = get_fields(layer)
    table = [row for row in arcpy.da.SearchCursor(layer, fields)]
    result_df = pd.DataFrame(table, columns=fields)
    result_df = result_df.set_index(fields[0])
    return result_df
