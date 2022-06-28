import arcpy
import pandas as pd


def layer_to_df(layer):
    fields = [field.name for field in arcpy.ListFields(layer)]
    table = [row for row in arcpy.da.SearchCursor(layer, fields)]
    df = pd.DataFrame(table, columns=fields)
    df.set_index(fields[0], inplace=True)
    return df
