import subprocess

import arcpy
import arcpy.analysis
import arcpy.management
import arcpy.sa
import pandas as pd

from biotools import arcutils, pdplus


def evaluate_habitat_size(biotope_layer, lower_bounds=(50, 10, 1, 0), scores=(1, 0.5, 0.3, 0.2, 0)):
    """H1 - 서식지 규모

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
    """H3 - 패치고립도
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


def run_maxent(**kwargs):
    command = f"java -mx512m -jar biotools/lib/maxent.jar {kwargs_to_command(kwargs)}"
    subprocess.run(command)
    return kwargs["outputdirectory"]
    # return "input/maxent_result/까마귀.asc"


def kwargs_to_command(kwargs):
    commands = [f"{param}={arg}" for param, arg in kwargs.items()]
    return " ".join(commands)


def evaluate_least_cost_distribution(biotope_layer, keystone_csv):
    """H4 - 서식지 연결성"""
    keystone_probability_asc = run_maxent(
        environmentallayers="path/to/env",
        samplesfile=keystone_csv,
        outputdirectory="path/to/result",
        #### Options of basicRun
        redoifexists=True,
        autorun=True,
        autofeature=True,
        responsecurves=True,
        jackknife=True,
        #### Options of advancdRun
        # writeplotdata=True,
        # appendtoresultsfile=False, # 결과파일(maxentResults.csv) 초기화(f)/추가(T)
        # writebackgroundpredictions=True
    )
    keystone_probability_raster = arcpy.management.CopyRaster(keystone_probability_asc, "memory/keystone_probability_raster")
    arcpy.management.DefineProjection(keystone_probability_raster, "biotools/res/ITRF_2000_UTM_K.prj")

    with arcpy.EnvManager(outputCoordinateSystem="biotools/res/WGS1984.prj"):
        result_table = arcpy.sa.ZonalStatisticsAsTable(
            biotope_layer, arcutils.get_oid_field(biotope_layer),
            keystone_probability_raster, "memory/result_table",
            "DATA", "MEAN", "CURRENT_SLICE")

    biotope_df = arcutils.layer_to_df(biotope_layer)
    result_df = arcutils.layer_to_df(result_table)

    result_df = result_df.assign(H4_RESULT=lambda x: 1 - x["MEAN"])
    result_df = result_df.drop(columns=["MEAN"])
    result_df = result_df.rename(columns={
        "COUNT": "H4_COUNT",
        "AREA": "H4_AREA",
    })
    return pdplus.left_merge_with_default(biotope_df, result_df, on="FID", default=0)


def evaluate_occurrence_of_piece_of_land(biotope_layer, commercial_point_layer, cell_size=0.00001):
    """H5 - 자투리땅 발생 가능성

    Option: 경기도 전체에서 Euq하면 계산 처리가 불가능할 수도 있으니 비오톱 지도 범위만 선택해서 Euclidean Distance를 하는게 좋음.
    CellSize: Defalt는 1m. 분석지역의 비오톱지도 중 가장 작은 비오톱에 하나 이상의 셀이 들어갈 수 있도록 설정함.
    가장 작은 비오톱보다 셀 사이즈가 크면 Zonal Statistics에서 계산 못함.
    (ITRF -> 1, WGS -> 0.00001)
    """
    selected_commercial_point_layer = arcpy.management.SelectLayerByLocation(commercial_point_layer, "INTERSECT", biotope_layer, "5 Kilometers")
    distance_raster = arcpy.sa.EucDistance(selected_commercial_point_layer, cell_size=cell_size)

    result_table = arcpy.sa.ZonalStatisticsAsTable(
        biotope_layer, "FID", distance_raster, "memory/result_table", "DATA", "MINIMUM", "CURRENT_SLICE", 90, "AUTO_DETECT")

    biotope_df = arcutils.layer_to_df(biotope_layer)
    result_df = arcutils.layer_to_df(result_table)

    max_distance = result_df["MIN"].max()
    result_df = result_df.assign(result=lambda x: x["MIN"] / max_distance)
    result_df = result_df.rename(columns={
        "COUNT": "H5_COUNT",
        "AREA": "H5_AREA",
        "MIN": "H5_MIN",
        "result": "H5_RESULT"
    })
    return pdplus.left_merge_with_default(biotope_df, result_df, on="FID", default=0)
