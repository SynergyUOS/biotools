import arcpy.management
import pandas as pd

from biotools import foodchain, habitat


def main():
    biotope_layer = arcpy.management.MakeFeatureLayer("path/to/biotope_map.shp", "biotope_layer")
    survey_point_layer = arcpy.management.MakeFeatureLayer("path/to/survey_point.shp", "survey_point_layer")
    species_info_df = pd.read_csv("path/to/species_info.csv", encoding="cp949")
    commercial_point_layer = arcpy.management.XYTableToPoint(
        "path/to/commercial_point.csv", "memory/commercial_point_layer", "경도", "위도", coordinate_system="path/to/GCS_WGS_1984.prj")

    result_df = habitat.evaluate_habitat_size(biotope_layer)
    print(result_df.head())

    result_df = habitat.evaluate_patch_isolation(biotope_layer)
    print(result_df.sort_values("PatchIsolation", ascending=False).head())

    # result_df = habitat.evaluate_least_cost_distribution(biotope_layer, "path/to/keystone.csv")
    # print(result_df.head())

    result_df = habitat.evaluate_occurrence_of_piece_of_land(biotope_layer, commercial_point_layer, cell_size=0.001)
    print(result_df.sort_values("H5_RESULT", ascending=False).head())

    # result_df = habitat.evaluate_availability_of_piece_of_land(biotope_layer, "input/maxent_result/까마귀.asc")
    # print(result_df.sort_values("H6_RESULT", ascending=False))

    result_df = foodchain.evaluate_number_of_food_resources(biotope_layer, survey_point_layer, species_info_df)
    print(result_df.sort_values("All_Snumber", ascending=False).head())

    result_df = foodchain.evaluate_number_of_food_resources(biotope_layer, survey_point_layer, species_info_df, one_per_point=False)
    print(result_df.sort_values("All_Snumber", ascending=False).head())

    result_df = foodchain.evaluate_diversity_index(biotope_layer, survey_point_layer, species_info_df)
    print(result_df.sort_values("2_Diversity_Index", ascending=False).head())

    result_df = foodchain.evaluate_combinable_producers_and_consumers(biotope_layer, survey_point_layer, species_info_df)
    print(result_df.sort_values("3_Combinable_Producers_and_Consumers", ascending=False).head())

    result_df = foodchain.evaluate_connection_strength(biotope_layer, survey_point_layer, species_info_df)
    print(result_df.sort_values("Prey_Snumber", ascending=False).head())

    result_df = foodchain.evaluate_similar_functional_species(biotope_layer, survey_point_layer, species_info_df)
    print(result_df.sort_values("Alt_S", ascending=False).head())


if __name__ == "__main__":
    main()
