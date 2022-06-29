import arcpy.management
import pandas as pd

from biotools import foodchain, habitat


def main():
    biotope_layer = arcpy.management.MakeFeatureLayer("path/to/biotope_map.shp", "biotope_layer")
    survey_point_layer = arcpy.management.MakeFeatureLayer("path/to/survey_point.shp", "survey_point_layer")
    species_info_df = pd.read_csv("path/to/species_info.csv", encoding="cp949")

    result_df = foodchain.get_number_of_food_resources(biotope_layer, survey_point_layer, species_info_df)
    print(result_df.sort_values("All_Snumber", ascending=False).head())

    result_df = foodchain.get_number_of_food_resources(biotope_layer, survey_point_layer, species_info_df, one_per_point=False)
    print(result_df.sort_values("All_Snumber", ascending=False).head())

    result_df = habitat.get_habitat_size(biotope_layer)
    print(result_df.head())

    result_df = habitat.get_patch_isolation(biotope_layer)
    print(result_df.sort_values("PatchIsolation", ascending=False).head())


if __name__ == "__main__":
    main()
