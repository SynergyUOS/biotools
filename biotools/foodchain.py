import math
from os import PathLike
from pathlib import Path


import arcpy
import arcpy.analysis
import arcpy.management
import arcpy.sa
import pandas as pd

from biotools import arcutils, maxent, pdplus


def _get_enriched_survey_point_df(survey_point_layer, biotope_layer, species_info_df: pd.DataFrame) -> pd.DataFrame:
    """
    BT_ID field will be added to `biotope_layer` permanently.
    SP_ID field will be added to `survey_point_layer` permanently.
    """
    if "SP_ID" not in arcutils.get_fields(survey_point_layer):
        arcpy.management.CalculateField(survey_point_layer, "SP_ID", f"'SP_ID!FID!'", expression_type="PYTHON3", field_type="TEXT")

    if "BT_ID" not in arcutils.get_fields(biotope_layer):
        arcpy.management.CalculateField(biotope_layer, "BT_ID", f"'BT_ID!FID!'", expression_type="PYTHON3", field_type="TEXT")

    joined_survey_point_layer = arcpy.analysis.SpatialJoin(survey_point_layer, biotope_layer, "memory/joined_survey_point_layer")

    survey_point_df = arcutils.shp_to_df(joined_survey_point_layer)
    survey_point_df = pd.merge(survey_point_df, species_info_df, how="inner", left_on="국명", right_on="S_Name") # how="left"?

    arcpy.management.Delete("memory/joined_survey_point_layer")

    return survey_point_df


def evaluate_number_of_food_resources(biotope_layer, survey_point_layer, species_info_df: pd.DataFrame, one_per_point=True) -> pd.DataFrame:
    """F1 - 먹이자원 개체수

    종 출현 정보 Point SHP는 전처리로 먹이자원종을 먼저 설정해줘야 함.
    이 코드에서는 임위로 먹이종(곤충, 육상곤충, 포유류)을 1로, 아닌 종을 0으로 FR(Food Resources) 필드에 입력하였다.
    개체수 필드를 미리 숫자형 데이터로 변경시키고, 출현 정보는 있는데 NoData가 되어 있는 경우가 있으니, NoData를 미리 1로 채울 필요가 있음.
    """
    biotope_df = arcutils.shp_to_df(biotope_layer)
    survey_point_df = _get_enriched_survey_point_df(survey_point_layer, biotope_layer, species_info_df)

    table = []
    for bt_id in survey_point_df["BT_ID"].unique():
        if bt_id is None:
            continue

        if one_per_point:
            prey_count, total_count = _count_one_per_row(survey_point_df[survey_point_df["BT_ID"] == bt_id], "Owls_foods", "Prey_S")
        else:
            prey_count, total_count = _count_vary_per_row(survey_point_df[survey_point_df["BT_ID"] == bt_id], "Owls_foods", "Prey_S", "개체수")

        number_of_food_resources = prey_count / total_count
        table.append([bt_id, prey_count, total_count, number_of_food_resources])

    result_df = pd.DataFrame(table, columns=["BT_ID", "Prey_Snumber", "All_Snumber", "1_Number_of_Food_Resources"])
    result_df = pdplus.left_merge_with_default(biotope_df, result_df, "BT_ID", 0)
    return result_df


def _count_one_per_row(df: pd.DataFrame, field: str, target: str):
    seq = df[field].tolist()
    total_count = len(seq)
    target_count = seq.count(target)
    return target_count, total_count


def _count_vary_per_row(df: pd.DataFrame, field: str, target: str, count_field: str):
    count_s = pd.to_numeric(df[count_field], errors="coerce").fillna(1)
    total_count = count_s.sum()
    target_count = count_s[df[field] == target].sum()
    return target_count, total_count


def evaluate_diversity_index(biotope_layer, survey_point_layer, species_info_df: pd.DataFrame):
    """F2 - 생물다양성

    [Shannon Index](https://en.wikipedia.org/wiki/Diversity_index#Shannon_index)
    """
    biotope_df = arcutils.shp_to_df(biotope_layer)
    survey_point_df = _get_enriched_survey_point_df(survey_point_layer, biotope_layer, species_info_df)

    table = []
    for bt_id in survey_point_df["BT_ID"].unique():
        if bt_id is None:
            continue

        count_s = survey_point_df[survey_point_df["BT_ID"] == bt_id]["국명"].value_counts()
        shannon_index = _get_shannon_index(count_s)
        table.append([bt_id, count_s.sum(), shannon_index])

    result_df = pd.DataFrame(table, columns=["BT_ID", "ALL_number", "H"])
    result_df = result_df.assign(**{"2_Diversity_Index": lambda x: _minmax_normalize(x["H"])})

    result_df = pdplus.left_merge_with_default(biotope_df, result_df, "BT_ID", 0)
    return result_df


def _get_shannon_index(counts):
    proportions = [count / sum(counts) for count in counts]
    return sum(-(p * math.log2(p)) for p in proportions)


def _minmax_normalize(seq):
    maximum = max(seq)
    minimum = min(seq)
    return [(i - minimum) / (maximum - minimum) for i in seq]


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
        arcpy.management.Project(
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
        mean_raster = arcpy.sa.CellStatistics(
            [str(asc) for asc in ascs],
            "MEAN"
        )
        mean_raster.save(str(mean_tif))

    with arcpy.EnvManager(outputCoordinateSystem=arcutils.ITRF2000_PRJ):
        result_table = arcpy.sa.ZonalStatisticsAsTable(
            biotope_shp,
            "BT_ID",
            str(mean_tif),
            "memory/result_table",
            statistics_type="MEAN"
        )
    result_df = arcutils.shp_to_df(result_table)
    arcpy.management.Delete(result_table)

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
