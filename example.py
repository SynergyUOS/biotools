from biotools import arcutils, Biotools


def main():
    bt = Biotools(
        "path/to/BiotopeMap.shp",
        "path/to/result/"
    )
    h1 = bt.run_h1()
    print(arcutils.shp_to_df(h1))
    h2 = bt.run_h2()
    print(arcutils.shp_to_df(h2))
    h3 = bt.run_h3()
    print(arcutils.shp_to_df(h3))

    bt = Biotools(
        "path/to/BiotopeMap.shp",
        "path/to/result/",
        commercialpoint_csv="path/to/commercialpoint.csv"
    )
    h5 = bt.run_h5()
    print(arcutils.shp_to_df(h5))

    bt = Biotools(
        "path/to/BiotopeMap.shp",
        "path/to/result/",
        environmentallayer_directory="path/to/envlayer/",
        keystone_species_csv="path/to/keystone_species.csv"
    )
    h4 = bt.run_h4()
    print(arcutils.shp_to_df(h4))
    h6 = bt.run_h6()
    print(arcutils.shp_to_df(h6))


if __name__ == "__main__":
    main()
