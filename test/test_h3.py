from pathlib import Path
import shutil
import unittest

import pandas as pd

from biotools import arcutils, Biotools


class TestH3(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.temp_result_dir = Path("test/temp_result/")
        cls.bt = Biotools(
            "test/fixture/biotope.shp",
            cls.temp_result_dir
        )
        cls.bt.run_h3()

        cls.wgs = cls.temp_result_dir / "process/biotope_WGS.shp"
        cls.h3_shp = cls.temp_result_dir / "result_h3/biotope_WGS_h3.shp"
        cls.h3_csv = cls.temp_result_dir / "result_h3/biotope_WGS_h3.csv"

    def test_wgs_exists(self):
        self.assertTrue(self.wgs.exists)

    def test_wgs_correct(self):
        result = arcutils.shp_to_df(self.wgs)
        answer = arcutils.shp_to_df("test/answer/process1/biotope_WGS.shp")
        self.assertTrue(result.equals(answer))

    def test_shp_exists(self):
        self.assertTrue(self.h3_shp.exists())

    def test_shp_correct(self):
        result = arcutils.shp_to_df(self.h3_shp)
        answer = arcutils.shp_to_df("test/answer/result_h3/biotope_WGS_h3.shp")
        self.assertTrue(result.equals(answer))

    def test_csv_exists(self):
        self.assertTrue(self.h3_csv.exists())

    def test_csv_correct(self):
        result = pd.read_csv(self.h3_csv)
        answer = pd.read_csv("test/answer/result_h3/biotope_WGS_h3.csv")
        self.assertTrue(result.equals(answer))

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.temp_result_dir)
