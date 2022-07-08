import math
from os import PathLike
from pathlib import Path

import arcpy
import arcpy.analysis as aa
import arcpy.management as am
import arcpy.sa as asa
import pandas as pd

from biotools import arcutils, maxent, pdplus


class FoodResourceCount:

    def __init__(
        self,
        biotope_shp,
        surveypoint_shp,
        foodchin_info_csv,
        result_shp,
        skip_noname=True
    ):
        self._biotope_shp = str(biotope_shp)
        self._surveypoint_shp = str(surveypoint_shp)
        self._foodchain_info_df = pd.read_csv(foodchin_info_csv, encoding="euc-kr")
        self._result_shp = str(result_shp)
        self._skip_noname = skip_noname
        self._surverpoint = _Surveypoint(
            self._surveypoint_shp,
            self._biotope_shp,
            self._foodchain_info_df
        )

    def run(self):
        self._surverpoint.enrich(self._skip_noname)
        surveypoint_df = self._surverpoint.df

        table = []
        for bt_id, sub_df in surveypoint_df.groupby("BT_ID"):
            if bt_id is None:
                continue
            count_s = sub_df.groupby("Owls_foods").sum()["개체수"]
            total_count = count_s.sum()
            prey_count = count_s.get("Prey_S", 0)
            result = prey_count / total_count
            table.append([bt_id, prey_count, total_count, result])

        result_df = pd.DataFrame(
            table,
            columns=["BT_ID", "F1_PREY_N", "F1_TOTAL_N", "F1_RESULT"]
        )
        biotope_df = arcutils.shp_to_df(self._biotope_shp)
        result_df = biotope_df[["BT_ID"]].merge(result_df, how="left", on="BT_ID")
        result_df = result_df.fillna({"F1_RESULT": 0})
        return arcutils.clean_join(self._biotope_shp, result_df, self._result_shp)


class DiversityIndex:

    def __init__(
        self,
        biotope_shp,
        surveypoint_shp,
        foodchain_info_csv,
        result_shp,
        skip_noname=True
    ):
        self._biotope_shp = str(biotope_shp)
        self._surveypoint_shp = str(surveypoint_shp)
        self._foodchain_info_df = pd.read_csv(foodchain_info_csv, encoding="euc-kr")
        self._result_shp = str(result_shp)
        self._skip_noname = skip_noname
        self._surverpoint = _Surveypoint(
            self._surveypoint_shp,
            self._biotope_shp,
            self._foodchain_info_df
        )

    def run(self):
        self._surverpoint.enrich(self._skip_noname)
        surveypoint_df = self._surverpoint.df

        table = []
        for bt_id, sub_df in surveypoint_df.groupby("BT_ID"):
            if bt_id is None:
                continue
            count_s = sub_df[sub_df["Owls_foods"] == "Prey_S"].groupby("국명").sum()["개체수"]
            shannon_index = self._get_shannon_index(count_s)
            table.append([bt_id, count_s.sum(), shannon_index])

        result_df = pd.DataFrame(table, columns=["BT_ID", "F2_PREY_N", "F2_SHANNON"])
        result_df = result_df.assign(
            F2_RESULT=lambda x: self._minmax_normalize(x["F2_SHANNON"])
        )
        biotope_df = arcutils.shp_to_df(self._biotope_shp)
        result_df = biotope_df[["BT_ID"]].merge(result_df, how="left", on="BT_ID")
        result_df = result_df.fillna({"F2_RESULT": 0})
        return arcutils.clean_join(self._biotope_shp, result_df, self._result_shp)

    def _get_shannon_index(self, counts):
        total = sum(counts)
        proportions = [count / total for count in counts]
        return sum(-(p * math.log2(p)) for p in proportions)

    def _minmax_normalize(self, seq):
        maximum = max(seq)
        minimum = min(seq)
        return [(i - minimum) / (maximum - minimum) for i in seq]


class CombinableProducersAndConsumers:

    def __init__(
        self,
        biotope_shp,
        surveypoint_shp,
        foodchain_info_csv,
        result_shp,
    ):
        self._biotope_shp = str(biotope_shp)
        self._surveypoint_shp = str(surveypoint_shp)
        self._foodchain_info_csv = str(foodchain_info_csv)
        self._result_shp = str(result_shp)

    def run(self):
        pass
        # return arcutils.clean_join(self._biotope_shp, result_df, self._result_shp)


class ConnectionStrength:

    def __init__(
        self,
        biotope_shp,
        surveypoint_shp,
        foodchain_info_csv,
        result_shp,
    ):
        self._biotope_shp = str(biotope_shp)
        self._surveypoint_shp = str(surveypoint_shp)
        self._foodchain_info_csv = str(foodchain_info_csv)
        self._result_shp = str(result_shp)

    def run(self):
        pass
        # return arcutils.clean_join(self._biotope_shp, result_df, self._result_shp)


class SimilarFunctionalSpecies:

    def __init__(
        self,
        biotope_shp,
        surveypoint_shp,
        foodchain_info_csv,
        result_shp,
    ):
        self._biotope_shp = str(biotope_shp)
        self._surveypoint_shp = str(surveypoint_shp)
        self._foodchain_info_csv = str(foodchain_info_csv)
        self._result_shp = str(result_shp)

    def run(self):
        pass
        # return arcutils.clean_join(self._biotope_shp, result_df, self._result_shp)


class FoodResourceInhabitation:

    def __init__(
        self,
        biotope_shp,
        surveypoint_shp,
        foodchain_info_csv,
        result_shp,
    ):
        self._biotope_shp = str(biotope_shp)
        self._surveypoint_shp = str(surveypoint_shp)
        self._foodchain_info_csv = str(foodchain_info_csv)
        self._result_shp = str(result_shp)

    def run(self):
        pass
        # return arcutils.clean_join(self._biotope_shp, result_df, self._result_shp)


def _get_enriched_survey_point_df(survey_point_layer, biotope_layer, species_info_df: pd.DataFrame) -> pd.DataFrame:
    """
    BT_ID field will be added to `biotope_layer` permanently.
    SP_ID field will be added to `survey_point_layer` permanently.
    """
    if "SP_ID" not in arcutils.get_fields(survey_point_layer):
        am.CalculateField(survey_point_layer, "SP_ID", f"'SP_ID!FID!'", expression_type="PYTHON3", field_type="TEXT")

    if "BT_ID" not in arcutils.get_fields(biotope_layer):
        am.CalculateField(biotope_layer, "BT_ID", f"'BT_ID!FID!'", expression_type="PYTHON3", field_type="TEXT")

    joined_survey_point_layer = aa.SpatialJoin(survey_point_layer, biotope_layer, "memory/joined_survey_point_layer")

    survey_point_df = arcutils.shp_to_df(joined_survey_point_layer)
    survey_point_df = pd.merge(survey_point_df, species_info_df, how="inner", left_on="국명", right_on="S_Name") # how="left"?

    am.Delete("memory/joined_survey_point_layer")

    return survey_point_df


def evaluate_combinable_producers_and_consumers(biotope_layer, survey_point_layer, species_info_df: pd.DataFrame, scores: dict = None):
    """F3 - 조합가능한 생산자와 소비자 (영양레벨)"""
    if scores is None:
        scores = {
            3: 1.0,
            2: 0.6,
            1: 0.3
        }

    biotope_df = arcutils.shp_to_df(biotope_layer)
    survey_point_df = _get_enriched_survey_point_df(survey_point_layer, biotope_layer, species_info_df)

    table = []
    for bt_id in survey_point_df["BT_ID"].unique():
        if bt_id is None:
            continue

        count_s = survey_point_df[survey_point_df["BT_ID"] == bt_id]["D_Level"].value_counts()
        d1_count = count_s.get("D1", 0)
        d2_count = count_s.get("D2", 0)
        d3_count = count_s.get("D3", 0)
        score = scores[count_s.count()]
        table.append([bt_id, d1_count, d2_count, d3_count, score])

    result_df = pd.DataFrame(table, columns=["BT_ID", "D1_count", "D2_count", "D3_count", "3_Combinable_Producers_and_Consumers"])
    result_df = pdplus.left_merge_with_default(biotope_df, result_df, "BT_ID", 0)
    return result_df


def evaluate_connection_strength(biotope_layer, survey_point_layer, species_info_df: pd.DataFrame):
    """F4 - 연결강도"""
    biotope_df = arcutils.shp_to_df(biotope_layer)
    survey_point_df = _get_enriched_survey_point_df(survey_point_layer, biotope_layer, species_info_df)

    table = []
    for bt_id in survey_point_df["BT_ID"].unique():
        if bt_id is None:
            continue

        count_s = survey_point_df[survey_point_df["BT_ID"] == bt_id]["Owls_foods"].value_counts()
        prey_count = count_s.get("Prey_S", 0)
        table.append([bt_id, prey_count, int(prey_count > 0)])

    result_df = pd.DataFrame(table, columns=["BT_ID", "Prey_Snumber", "4_Connection_Strength"])
    result_df = pdplus.left_merge_with_default(biotope_df, result_df, "BT_ID", 0)
    return result_df


def evaluate_similar_functional_species(biotope_layer, survey_point_layer, species_info_df):
    """F5 - 유사기능종"""
    biotope_df = arcutils.shp_to_df(biotope_layer)
    survey_point_df = _get_enriched_survey_point_df(survey_point_layer, biotope_layer, species_info_df)

    table = []
    for bt_id in survey_point_df["BT_ID"].unique():
        if bt_id is None:
            continue

        count_s = survey_point_df.loc[survey_point_df["BT_ID"] == bt_id]["Alternative_S"].value_counts()
        threatened_count = count_s.get("Threatened_S", 0)
        alt_alien_count = count_s.get("Alt_Alien_S", 0)
        alt_count = count_s.get("Alt_S", 0)
        normal_count = count_s.get("Normal_S", 0)

        if alt_count > 0:
            similar_functional_species = 1
        elif alt_alien_count > 0:
            similar_functional_species = 0.5
        else:
            similar_functional_species = 0

        table.append([bt_id, threatened_count, alt_alien_count, alt_count, normal_count, similar_functional_species])

    result_df = pd.DataFrame(table, columns=["BT_ID", "Threatened_S", "Alt_Alien_S", "Alt_S", "Normal_S", "5_Similar_Functional_Species"])
    result_df = pdplus.left_merge_with_default(biotope_df, result_df, "BT_ID", 0)
    return result_df


def evaluate_inhabitation_of_food_resources(
    biotope_shp: PathLike,
    surveypoint_shp: PathLike,
    environmentallayer_directory: PathLike,
    result_directory: PathLike
):
    """F6 - 먹이자원 서식확률"""
    base_dir = Path(result_directory)
    process_dir = base_dir / "process"
    result_dir = base_dir / "f6_result"

    process_dir.mkdir(parents=True, exist_ok=True)
    result_dir.mkdir(parents=True, exist_ok=True)

    new_name = augment_name(Path(surveypoint_shp).name, "_ITRF")
    surveypoint_itrf_shp = process_dir / new_name

    if not surveypoint_itrf_shp.exists():
        am.Project(
            surveypoint_shp,
            str(process_dir / new_name),
            arcutils.ITRF2000_PRJ
        )


    surveypoint_itrf_df = arcutils.shp_to_df(surveypoint_itrf_shp)
    sample_df = surveypoint_itrf_df[["국명", "Shape"]]
    sample_df = sample_df.assign(
        LONGITUDE=lambda x: x["Shape"].apply(lambda x: x[0]),
        LATITUDE=lambda x: x["Shape"].apply(lambda x: x[1]),
    )
    sample_df = sample_df.drop(columns="Shape")

    sample_name = augment_name(surveypoint_itrf_shp, "_sample").with_suffix(".csv")
    sample_csv = process_dir / sample_name
    sample_df.to_csv(sample_csv, index=False, encoding="euc-kr")


    ascs = maxent.run_maxent(
        sample_csv,
        environmentallayer_directory,
        process_dir / (sample_csv.stem + "_maxent"),
    )

    mean_name = augment_name(sample_name, "_maxent_mean").with_suffix(".tif")
    mean_tif = process_dir / mean_name

    if not mean_tif.exists():
        mean_raster = asa.CellStatistics(
            [str(asc) for asc in ascs],
            "MEAN"
        )
        mean_raster.save(str(mean_tif))

    with arcpy.EnvManager(outputCoordinateSystem=arcutils.ITRF2000_PRJ):
        result_table = asa.ZonalStatisticsAsTable(
            biotope_shp,
            "BT_ID",
            str(mean_tif),
            "memory/result_table",
            statistics_type="MEAN"
        )
    result_df = arcutils.shp_to_df(result_table)
    am.Delete(result_table)

    result_df = result_df.rename(columns={
        "COUNT": "F6_COUNT",
        "AREA": "F6_AREA",
        "MEAN": "F6_RESULT",
    })
    result_df = result_df.drop(columns="ZONE_CODE")

    biotope_df = arcutils.shp_to_df(biotope_shp)
    result_df = biotope_df.merge(result_df, how="left", on="BT_ID")
    result_df = result_df.fillna({"F6_RESULT": 0})
    return result_df


def augment_name(path: PathLike, word: str) -> Path:
    path = Path(path)
    return path.with_stem(path.stem + word)


class _Surveypoint:

    def __init__(self, surveypoint_shp, biotope_shp, foodchain_info_df):
        self._biotope_shp = str(biotope_shp)
        self._surveypoint_shp = str(surveypoint_shp)
        self._foodchain_info_df = foodchain_info_df
        self._surverpoint_df = arcutils.shp_to_df(surveypoint_shp)

    @property
    def df(self):
        return self._surverpoint_df

    def enrich(self, skip_noname=True):
        joined = aa.SpatialJoin(self._surveypoint_shp, self._biotope_shp, "memory/joined")
        self._surverpoint_df = arcutils.shp_to_df(joined)
        am.Delete(joined)

        self._surverpoint_df = pd.merge(
            self._surverpoint_df,
            self._foodchain_info_df,
            how="left",
            left_on="국명",
            right_on="S_Name"
        )

        if skip_noname:
            self._surverpoint_df = pdplus.drop_if(
                self._surverpoint_df,
                lambda x: x["국명"] == " "
            )
        else:
            self._surverpoint_df = pdplus.replace_row(
                self._surverpoint_df,
                {
                    "국명": "Noname",
                    "Owls_foods": "Normal_S",
                    "D_Level": "D3",
                    "Alternative_s": "Normal_S"
                },
                lambda x: x["국명"] == " "
            )

        self._surverpoint_df["개체수"] = pd.to_numeric(
            self._surverpoint_df["개체수"],
            errors="coerce"
        ).fillna(1)