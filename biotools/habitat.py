import arcpy.analysis
import arcpy.management
import pandas as pd

from biotools import arcutils


def evaluate_habitat_size(biotope_layer, lower_bounds=(50, 10, 1, 0), scores=(1, 0.5, 0.3, 0.2, 0)):
    """서식지 규모

    ### To Do
    * arcpy로 비오톱 합치기
    * class 형태로 묶기
    * 패키지 설치 포함하여 작업하기, if 문 이용하여 설치 안되어 있으면 설치되는 것으로
    """
    biotope_df = arcutils.layer_to_df(biotope_layer)
    return biotope_df.assign(HaArea=lambda x: x["Area"] / 10000,
                             Ix_BioScale=lambda x: x["HaArea"].apply(_range_evaluate, lower_bounds=lower_bounds, scores=scores))


def _range_evaluate(value, lower_bounds, scores):
    for i, lower_bound in enumerate(lower_bounds):
        if value >= lower_bound:
            return scores[i]
    return scores[-1]


def get_default_habitable_codes():
    result = []
    for category, upper_bound in zip("HIJKLM", (12, 1, 13, 2, 5, 4)):
        result += [category + str(i) for i in range(1, upper_bound + 1)]
    return tuple(result)


def evaluate_patch_isolation(biotope_layer, habitable_codes=get_default_habitable_codes()):
    """패치고립도
    """
    query = " OR ".join([f"비오톱 = '{code}'" for code in habitable_codes])
    arcpy.management.SelectLayerByAttribute(biotope_layer, "NEW_SELECTION", query)

    buffer_layer = arcpy.analysis.Buffer(biotope_layer, "memory/buffer_layer", "125 Meters", "FULL", "ROUND", "NONE")
    in_buffer_table = arcpy.analysis.TabulateIntersection(buffer_layer, "ORIG_FID", biotope_layer,
                                                          "memory/in_buffer_table", "FID", out_units="SQUARE_METERS")

    arcpy.management.SelectLayerByAttribute(biotope_layer, "CLEAR_SELECTION")

    biotope_df = arcutils.layer_to_df(biotope_layer)
    in_buffer_df = arcutils.layer_to_df(in_buffer_table)

    in_buffer_proportion_s = in_buffer_df.groupby("ORIG_FID").sum()["PERCENTAGE"]

    result_df = pd.merge(biotope_df, in_buffer_proportion_s, left_index=True, right_index=True, how="left")
    result_df = result_df.rename(columns={"PERCENTAGE": "PatchIsolation"})
    result_df = result_df.fillna({"PatchIsolation": 0})

    arcpy.management.Delete("memory/buffer_layer")
    arcpy.management.Delete("memory/in_buffer_table")

    return result_df