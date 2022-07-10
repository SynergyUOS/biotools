from biotools import arcutils, Biotools


def main():
    # bt = Biotools(
    #     "path/to/BiotopeMap.shp",
    #     "path/to/result/"
    # )
    # h1 = bt.run_h1()
    # print(arcutils.shp_to_df(h1))
    # h2 = bt.run_h2()
    # print(arcutils.shp_to_df(h2))
    # h3 = bt.run_h3()
    # print(arcutils.shp_to_df(h3))

    # bt = Biotools(
    #     "path/to/BiotopeMap.shp",
    #     "path/to/result/",
    #     environmentallayer_directory="path/to/envlayer/",
    #     keystone_species_csv="path/to/keystone_species.csv"
    # )
    # h4 = bt.run_h4()
    # print(arcutils.shp_to_df(h4))
    # h6 = bt.run_h6()
    # print(arcutils.shp_to_df(h6))

    # bt = Biotools(
    #     "path/to/BiotopeMap.shp",
    #     "path/to/result/",
    #     commercialpoint_csv="path/to/commercialpoint.csv"
    # )
    # h5 = bt.run_h5()
    # print(arcutils.shp_to_df(h5))

    bt = Biotools(
        "path/to/BiotopeMap.shp",
        "path/to/result/",
        surveypoint_shp="path/to/Surveypoint.shp",
        foodchain_info_csv="path/to/foodchain_info.csv"
    )
    # f1 = bt.run_f1()
    # print(arcutils.shp_to_df(f1))
    # f2 = bt.run_f2()
    # print(arcutils.shp_to_df(f2))
    f3 = bt.run_f3()
    print(arcutils.shp_to_df(f3))
    # f4 = bt.run_f4()
    # print(arcutils.shp_to_df(f4))
    # f5 = bt.run_f5()
    # print(arcutils.shp_to_df(f5))

    # bt = Biotools(
    #     "path/to/BiotopeMap.shp",
    #     "path/to/result/",
    #     environmentallayer_directory="path/to/envlayer/",
    #     surveypoint_shp="path/to/Surveypoint.shp",
    #     foodchain_info_csv="path/to/foodchain_info.csv"
    # )
    # f6 = bt.run_f6()
    # print(arcutils.shp_to_df(f6))

    # full = bt.merge()
    # print(arcutils.shp_to_df(full))


if __name__ == "__main__":
    main()
