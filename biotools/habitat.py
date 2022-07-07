from os import PathLike
from pathlib import Path
from typing import Sequence, Union

import arcpy
import arcpy.analysis
import arcpy.management

import arcpy.analysis as aa
import arcpy.management as am
import arcpy.sa as asa
import arcpy.sa
import numpy as np
import pandas as pd

from biotools import arcutils, pdplus, maxent


class HabitatSize:

    def __init__(
        self,
        biotope_shp,
        result_shp,
        sized_shp,
        lower_bounds,
        scores
    ):
        """
        biotope_shp: must have BT_ID field. condisdered WGS 1984.
        """
        self._biotope_shp = str(biotope_shp)
        self._result_shp = str(result_shp)
        self._sized_shp = str(sized_shp)
        self._lower_bounds = lower_bounds
        self._scores = scores

    def run(self):
        if not Path(self._sized_shp).exists():
            medium_codes = arcutils.get_medium_codes([9, 10, 12, 13, 14, 15])
            query = arcutils.query_isin("비오톱", medium_codes)
            selected = am.SelectLayerByAttribute(self._biotope_shp, "NEW_SELECTION", query)
            with arcpy.EnvManager(outputCoordinateSystem=arcutils.WGS1984_PRJ):
                dissolved = am.Dissolve(
                    selected,
                    "memory/dissolved",
                    dissolve_field="비오톱",
                    multi_part="SINGLE_PART"
                )

            am.CalculateGeometryAttributes(
                dissolved,
                [["H1_HECTARES", "AREA_GEODESIC"]],
                area_unit="HECTARES",
            )

            with arcpy.EnvManager(outputCoordinateSystem=arcutils.WGS1984_PRJ):
                arcpy.analysis.SpatialJoin(
                    self._biotope_shp,
                    dissolved,
                    self._sized_shp,
                )
            am.Delete(dissolved)

        result_df = arcutils.shp_to_df(self._sized_shp)
        result_df = result_df[["BT_ID", "H1_HECTARE"]]
        result_df = result_df.assign(
            H1_RESULT=lambda x: x["H1_HECTARE"].apply(self._range_evaluate)
        )
        return arcutils.clean_join(self._biotope_shp, result_df, self._result_shp)

    def _range_evaluate(self, value):
        if np.isnan(value):
            return 0

        for i, lower_bound in enumerate(self._lower_bounds):
            if value >= lower_bound:
                return self._scores[i]
        return 0        # minus area unreachable


class StructuredLayer:

    def __init__(
        self,
        biotope_shp,
        result_shp,
        scores
    ):
        self._biotope_shp = str(biotope_shp)
        self._result_shp = str(result_shp)
        self._scores = scores

    def run(self):
        biotope_df = arcutils.shp_to_df(self._biotope_shp)
        is_green_s = ~biotope_df["비오톱"].isin(arcutils.get_medium_codes(range(1, 9)))

        structure_df = self._create_dummy_structure()
        green_df = structure_df[is_green_s]
        green_df = self._score_structured_layer(green_df)
        green_df = green_df.rename(columns={
            "HERB": "H2_HERB",
            "SHRUB": "H2_SHRUB",
            "TREE": "H2_TREE",
        })
        result_df = biotope_df[["BT_ID"]].merge(green_df, how="left", on="BT_ID")
        result_df = result_df.fillna({"H2_RESULT": 0})
        return arcutils.clean_join(self._biotope_shp, result_df, self._result_shp)

    def _create_dummy_structure(self):
        import random
        biotope_df = arcutils.shp_to_df(self._biotope_shp)
        return biotope_df[["BT_ID"]].assign(
            HERB=random.choices(["N", "Y"], weights=[1, 1], k=len(biotope_df)),
            SHRUB=random.choices(["N", "Y"], weights=[3, 1], k=len(biotope_df)),
            TREE=random.choices(["N", "Y"], weights=[4, 1], k=len(biotope_df))
        )

    def _score_structured_layer(self, df: pd.DataFrame):
        result_df = df.copy()
        p = (df["HERB"] == "Y")
        q = (df["SHRUB"] == "Y")
        r = (df["TREE"] == "Y")
        score_s = p.astype(int) + q.astype(int) + r.astype(int)
        score_s = score_s.apply(lambda x: self._scores[x - 1])
        result_df = result_df.assign(H2_RESULT=score_s)
        return result_df


class PatchIsolation:

    def __init__(
        self,
        biotope_shp,
        result_shp
    ):
        self._biotope_shp = str(biotope_shp)
        self._result_shp = str(result_shp)

    def run(self):
        with arcpy.EnvManager(outputCoordinateSystem=arcutils.ITRF2000_PRJ):
            buffer_layer = aa.Buffer(
                self._biotope_shp,
                "memory/buffer_layer",
                "125 Meters"
            )

        medium_codes = arcutils.get_medium_codes([9, 10, 12, 13, 14, 15])
        query = arcutils.query_isin("비오톱", medium_codes)
        selected = am.SelectLayerByAttribute(self._biotope_shp, "NEW_SELECTION", query)
        with arcpy.EnvManager(outputCoordinateSystem=arcutils.ITRF2000_PRJ):
            dissolved = am.Dissolve(
                selected,
                "memory/dissolved",
            )

        with arcpy.EnvManager(outputCoordinateSystem=arcutils.ITRF2000_PRJ):
            in_buffer_table = aa.TabulateIntersection(
                buffer_layer,
                "BT_ID",
                dissolved,
                "memory/in_buffer_table",
                out_units="SQUARE_METERS"
            )
        result_df = arcutils.shp_to_df(in_buffer_table)
        am.Delete(in_buffer_table)
        am.Delete(buffer_layer)
        am.Delete(dissolved)

        result_df = result_df.rename(columns={
            "AREA": "H3_AREA",
            "PERCENTAGE": "H3_RESULT"
        })
        biotope_df = arcutils.shp_to_df(self._biotope_shp)
        result_df = biotope_df[["BT_ID"]].merge(result_df, how="left", on="BT_ID")
        result_df = result_df.fillna({"H3_RESULT": 0})
        return arcutils.clean_join(self._biotope_shp, result_df, self._result_shp)


class LeastcostDistribution:

    def __init__(
        self,
        biotope_shp,
        result_shp
    ):
        self._biotope_shp = str(biotope_shp)
        self._result_shp = str(result_shp)

    def run(self):
        pass


class PieceoflandOccurrence:

    def __init__(
        self,
        biotope_shp,
        commercialpoint_csv,
        result_shp,
        cellsize
    ):
        self._biotope_shp = str(biotope_shp)
        self._result_shp = str(result_shp)
        self._commercialpoint_csv = str(commercialpoint_csv)
        self._cellsize = cellsize

    def run(self):
        commercialpoint_layer = am.XYTableToPoint(
            self._commercialpoint_csv,
            "memory/commercialpoint_layer",
            "경도",
            "위도",
            coordinate_system=arcutils.WGS1984_PRJ)

        selected = am.SelectLayerByLocation(
            commercialpoint_layer,
            "INTERSECT",
            self._biotope_shp,
            "5 Kilometers"
        )

        with arcpy.EnvManager(outputCoordinateSystem=arcutils.ITRF2000_PRJ):
            distance_raster = asa.EucDistance(selected, cell_size=self._cellsize)
        am.Delete(commercialpoint_layer)

        with arcpy.EnvManager(outputCoordinateSystem=arcutils.ITRF2000_PRJ):
            result_table = asa.ZonalStatisticsAsTable(
                self._biotope_shp,
                "BT_ID",
                distance_raster,
                "memory/result_table",
                statistics_type="MINIMUM",
            )
        result_df = arcutils.shp_to_df(result_table)
        am.Delete(result_table)

        max_distance = result_df["MIN"].max()
        result_df = result_df.assign(H5_RESULT=lambda x: x["MIN"] / max_distance)
        result_df = result_df.drop(columns="ZONE_CODE")
        result_df = result_df.rename(columns={
            "COUNT": "H5_COUNT",
            "AREA": "H5_AREA",
            "MIN": "H5_MIN",
        })
        biotope_df = arcutils.shp_to_df(self._biotope_shp)
        result_df = biotope_df[["BT_ID"]].merge(result_df, how="left", on="BT_ID")
        result_df = result_df.fillna({"H5_RESULT": 0})
        return arcutils.clean_join(self._biotope_shp, result_df, self._result_shp)


class PieceoflandAvailability:

    def __init__(
        self,
        biotope_shp,
        result_shp
    ):
        self._biotope_shp = str(biotope_shp)
        self._result_shp = str(result_shp)

    def run(self):
        pass


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
    result_df = arcutils.shp_to_df(result_table)
    arcpy.management.Delete(result_table)

    result_df = result_df.assign(H4_RESULT=lambda x: 1 - x["MEAN"])
    result_df = result_df.drop(columns=["MEAN", "ZONE_CODE"])
    result_df = result_df.rename(columns={
        "COUNT": "H4_COUNT",
        "AREA": "H4_AREA",
    })
    biotope_df = arcutils.shp_to_df(biotope_shp)
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

    biotope_df = arcutils.shp_to_df(biotope_layer)
    result_df = arcutils.shp_to_df(result_table)

    max_distance = result_df["MIN"].max()
    result_df = result_df.assign(result=lambda x: x["MIN"] / max_distance)
    result_df = result_df.rename(columns={
        "COUNT": "H5_COUNT",
        "AREA": "H5_AREA",
        "MIN": "H5_MIN",
        "result": "H5_RESULT"
    })
    return pdplus.left_merge_with_default(biotope_df, result_df, on="FID", default=0)


def evaluate_availability_of_piece_of_land(
    biotope_shp: Union[str, PathLike],
    keystone_csv: Union[str, PathLike],
    environmentallayer_directory: Union[str, PathLike],
    result_directory: Union[str, PathLike]
):
    """H6 - 자투리땅 활용 가능성"""
    base_dir = Path(result_directory)
    process_dir = base_dir / "process"
    maxent_dir = process_dir / (Path(keystone_csv).stem + "_maxent")

    ascs = maxent.run_maxent(
        keystone_csv,
        environmentallayer_directory,
        maxent_dir
    )

    main_habitat_raster = arcpy.sa.Con(arcpy.Raster(str(ascs[0])) >= 0.5, 1)
    distance_raster = arcpy.sa.EucDistance(main_habitat_raster, cell_size=5)

    query = arcutils.make_isin_query("비오톱", [16])
    arcpy.management.SelectLayerByAttribute(biotope_shp, "NEW_SELECTION", query)

    with arcpy.EnvManager(outputCoordinateSystem=arcutils.ITRF2000_PRJ):
        result_table = arcpy.sa.ZonalStatisticsAsTable(
            biotope_shp,
            "BT_ID",
            distance_raster,
            "memory/result_table",
            statistics_type="MINIMUM"
        )

    arcpy.management.SelectLayerByAttribute(biotope_shp, "CLEAR_SELECTION")
    result_df = arcutils.shp_to_df(result_table)
    arcpy.management.Delete(result_table)

    maximum = result_df["MIN"].max()
    result_df = result_df.assign(H6_RESULT=lambda x: 1 - (x["MIN"] / maximum))
    result_df = result_df.rename(columns={
        "COUNT": "H6_COUNT",
        "AREA": "H6_AREA",
        "MIN": "H6_MIN",
    })
    result_df = result_df.drop(columns="ZONE_CODE")

    biotope_df = arcutils.shp_to_df(biotope_shp)
    result_df = pd.merge(biotope_df["BT_ID"], result_df, on="BT_ID", how="left")
    result_df = result_df.fillna({"H6_RESULT": 0})
    return result_df
