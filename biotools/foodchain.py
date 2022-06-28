import arcpy.analysis
import arcpy.management
import pandas as pd

from biotools import arcutils


def get_number_of_food_resources(biotope_layer, survey_point_layer, species_info_df: pd.DataFrame, one_per_point=True) -> pd.DataFrame:
    """먹이자원 개체수

    종 출현 정보 Point SHP는 전처리로 먹이자원종을 먼저 설정해줘야 함.
    이 코드에서는 임위로 먹이종(곤충, 육상곤충, 포유류)을 1로, 아닌 종을 0으로 FR(Food Resources) 필드에 입력하였다.
    개체수 필드를 미리 숫자형 데이터로 변경시키고, 출현 정보는 있는데 NoData가 되어 있는 경우가 있으니, NoData를 미리 1로 채울 필요가 있음.
    """
    arcpy.management.CalculateField(biotope_layer, "BT_ID", f"'BT_ID!FID!'", expression_type="PYTHON3", field_type="TEXT")
    arcpy.management.CalculateField(survey_point_layer, "SP_ID", f"'SP_ID!FID!'", expression_type="PYTHON3", field_type="TEXT")
    joined_survey_point_layer = arcpy.analysis.SpatialJoin(survey_point_layer, biotope_layer, "memory/joined_survey_point_layer")

    biotope_df = arcutils.layer_to_df(biotope_layer)
    survey_point_df = arcutils.layer_to_df(joined_survey_point_layer)
    survey_point_df = pd.merge(survey_point_df, species_info_df, how="inner", left_on="국명", right_on="S_Name") # how="left"?

    table = []
    for bt_id in survey_point_df["BT_ID"].unique():
        if bt_id is None:
            continue

        if one_per_point:
            prey_count, total_count = count_one_per_row(survey_point_df[survey_point_df["BT_ID"] == bt_id], "Owls_foods", "Prey_S")
        else:
            prey_count, total_count = count_vary_per_row(survey_point_df[survey_point_df["BT_ID"] == bt_id], "Owls_foods", "Prey_S", "개체수")

        number_of_food_resources = prey_count / total_count
        table.append([bt_id, prey_count, total_count, number_of_food_resources])

    columns = ["BT_ID", "Prey_Snumber", "All_Snumber", "1_Number_of_Food_Resources"]
    result_df = pd.DataFrame(table, columns=columns)
    result_df = pd.merge(biotope_df, result_df, on="BT_ID", how="left")
    result_df = result_df.fillna({field: 0 for field in columns[1:]})

    arcpy.management.Delete("memory/joined_survey_point_layer")

    return result_df

def count_one_per_row(df: pd.DataFrame, field: str, target: str):
    seq = df[field].tolist()
    total_count = len(seq)
    target_count = seq.count(target)
    return target_count, total_count

def count_vary_per_row(df: pd.DataFrame, field: str, target: str, count_field: str, ):
    count_s = pd.to_numeric(df[count_field], errors="coerce").fillna(1)
    total_count = count_s.sum()
    target_count = count_s[df[field] == target].sum()
    return target_count, total_count
