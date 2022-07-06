from os import PathLike
from pathlib import Path
from typing import Union

import arcpy
import arcpy.analysis
import arcpy.management
import arcpy.sa
import pandas as pd

from biotools import arcutils, pdplus, maxent


def evaluate_habitat_size(
    biotope_layer,
    lower_bounds=(50, 10, 1, 0),
    scores=(1, 0.5, 0.3, 0.2, 0)
) -> pd.DataFrame:
    """H1. 서식지 다양성 - 서식지 규모

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


def evaluate_structured_layer(biotope_shp):
    """H2. 서식지 다양성 - 층위구조"""
    arcutils.fix_fid(biotope_shp)

    biotope_df = arcutils.layer_to_df(biotope_shp)

    # temporary data creation
    import random
    result_df = biotope_df[["BT_ID"]].assign(
        HERB=random.choices(["N", "Y"], weights=[1, 1], k=len(biotope_df)),
        SHRUB=random.choices(["N", "Y"], weights=[3, 1], k=len(biotope_df)),
        TREE=random.choices(["N", "Y"], weights=[4, 1], k=len(biotope_df))
    )

    is_green_s = ~biotope_df["비오톱"].isin(arcutils.get_biotope_codes(range(1, 9)))
    green_df = result_df[is_green_s]
    green_df = _score_structured_layer(green_df)
    green_df = green_df.rename(columns={
        "HERB": "H2_HERB",
        "SHRUB": "H2_SHRUB",
        "TREE": "H2_TREE",
        "SCORE": "H2_RESULT"
    })
    result_df = biotope_df.merge(green_df, how="left", on="BT_ID")
    result_df = result_df.fillna({"H2_RESULT": 0})
    return result_df


def _score_structured_layer(df: pd.DataFrame, scores=(0.3, 0.6, 1)):
    result_df = df.copy()
    p = (df["HERB"] == "Y")
    q = (df["SHRUB"] == "Y")
    r = (df["TREE"] == "Y")
    score_s = p.astype(int) + q.astype(int) + r.astype(int)
    score_s = score_s.apply(lambda x: scores[x - 1])
    result_df = result_df.assign(SCORE=score_s)
    return result_df


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


def evaluate_least_cost_distribution(
    biotope_shp: Union[str, PathLike],
    keystone_csv: Union[str, PathLike],
    environmentallayer_directory: Union[str, PathLike],
    result_directory: Union[str, PathLike]
):
    """H4 - 서식지 연결성"""

    base_dir = Path(result_directory)
    process_dir = base_dir / "process"
    maxent_dir = process_dir / (Path(keystone_csv).stem + "_maxent")

    ascs = maxent.run_maxent(
        keystone_csv,
        environmentallayer_directory,
        maxent_dir
    )

    with arcpy.EnvManager(outputCoordinateSystem=arcutils.ITRF2000_PRJ):
        result_table = arcpy.sa.ZonalStatisticsAsTable(
            biotope_shp,
            "BT_ID",
            str(ascs[0]),
            "memory/result_table",
            statistics_type="MEAN"
        )
    result_df = arcutils.layer_to_df(result_table)
    arcpy.management.Delete(result_table)

    result_df = result_df.assign(H4_RESULT=lambda x: 1 - x["MEAN"])
    result_df = result_df.drop(columns=["MEAN", "ZONE_CODE"])
    result_df = result_df.rename(columns={
        "COUNT": "H4_COUNT",
        "AREA": "H4_AREA",
    })
    biotope_df = arcutils.layer_to_df(biotope_shp)
    result_df = biotope_df.merge(result_df, how="left", on="BT_ID")
    result_df = result_df.fillna({"H4_RESULT": 0})
    return result_df


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

    arcpy.management.SelectLayerByAttribute(biotope_layer, "CLEAR_SELECTION")

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


def evaluate_availability_of_piece_of_land(biotope_layer, keystone_probability_asc):
    """H6 - 자투리땅 활용 가능성"""
    # run maxent

    arcutils.fix_fid(biotope_layer)

    keystone_probability_raster = arcutils.load_asc(keystone_probability_asc,
                                                    arcutils.ITRF2000_PRJ)

    main_habitat_raster = arcpy.sa.Con(arcpy.Raster(keystone_probability_raster) >= 0.5, 1)
    distance_raster = arcpy.sa.EucDistance(main_habitat_raster, cell_size=30)

    query = arcutils.make_isin_query("비오톱", [16])
    arcpy.management.SelectLayerByAttribute(biotope_layer, "NEW_SELECTION", query)

    with arcpy.EnvManager(outputCoordinateSystem=arcutils.ITRF2000_PRJ):
        result_table = arcpy.sa.ZonalStatisticsAsTable(
            biotope_layer,
            "BT_ID",
            distance_raster,
            "memory/result_table",
            statistics_type="MINIMUM"
        )

    arcpy.management.SelectLayerByAttribute(biotope_layer, "CLEAR_SELECTION")
    arcpy.management.Delete(keystone_probability_raster)

    result_df = arcutils.layer_to_df(result_table)
    maximum = result_df["MIN"].max()
    result_df = result_df.assign(H6_RESULT=lambda x: 1 - (x["MIN"] / maximum))
    result_df = result_df.rename(columns={
        "COUNT": "H6_COUNT",
        "AREA": "H6_AREA",
        "MIN": "H6_MIN",
    })
    result_df = result_df.drop(columns="ZONE_CODE")

    biotope_df = arcutils.layer_to_df(biotope_layer)
    result_df = pd.merge(biotope_df["BT_ID"], result_df, on="BT_ID", how="left")
    result_df = result_df.fillna({"H6_RESULT": 0})
    return result_df
