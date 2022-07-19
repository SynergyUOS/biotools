from pathlib import Path
import shutil
import unittest

import pandas as pd

from biotools import arcutils, Biotools


class TestH5(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.temp_result_dir = Path("test/temp_result/")
        cls.bt = Biotools(
            "test/fixture/biotope.shp",
            cls.temp_result_dir,
            commercialpoint_csv="test/fixture/commercialpoint.csv"
        )
        cls.bt.run_h5()

        cls.wgs = cls.temp_result_dir / "process/biotope_WGS.shp"
        cls.shp = cls.temp_result_dir / "result_h5/biotope_WGS_h5.shp"
        cls.csv = cls.temp_result_dir / "result_h5/biotope_WGS_h5.csv"

    def test_wgs_exists(self):
        self.assertTrue(self.wgs.exists)

    def test_wgs_correct(self):
        result = arcutils.shp_to_df(self.wgs)
        answer = arcutils.shp_to_df("test/answer/process1/biotope_WGS.shp")
        self.assertTrue(result.equals(answer))

    def test_shp_exists(self):
        self.assertTrue(self.shp.exists())

    def test_shp_correct(self):
        result = arcutils.shp_to_df(self.shp)
        answer = arcutils.shp_to_df("test/answer/result_h5/biotope_WGS_h5.shp")
        self.assertTrue(result.equals(answer))

    def test_csv_exists(self):
        self.assertTrue(self.csv.exists())

    def test_csv_correct(self):
        result = pd.read_csv(self.csv)
        answer = pd.read_csv("test/answer/result_h5/biotope_WGS_h5.csv")
        self.assertTrue(result.equals(answer))

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.temp_result_dir)
