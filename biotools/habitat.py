from biotools import arcutils


def get_habitat_size(biotope_layer, lower_bounds=[50, 10, 1, 0], scores=[1, 0.5, 0.3, 0.2, 0]):
    """서식지 규모

    ### To Do
    * arcpy로 비오톱 합치기
    * class 형태로 묶기
    * 패키지 설치 포함하여 작업하기, if 문 이용하여 설치 안되어 있으면 설치되는 것으로
    """
    biotope_df = arcutils.layer_to_df(biotope_layer)
    return biotope_df.assign(HaArea=lambda x: x["Area"] / 10000,
                             Ix_BioScale=lambda x: x["HaArea"].apply(range_evaluate, lower_bounds=lower_bounds, scores=scores))

def range_evaluate(value, lower_bounds, scores):
    for i, lower_bound in enumerate(lower_bounds):
        if value >= lower_bound:
            return scores[i]
    return scores[-1]
