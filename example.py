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


if __name__ == "__main__":
    main()
