from pathlib import Path
import shutil
import unittest

import pandas as pd

from biotools import arcutils, Biotools


class TestF5(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.temp_result_dir = Path("test/temp_result/")
        cls.bt = Biotools(
            "test/fixture/biotope3.shp",
            cls.temp_result_dir,
            surveypoint_shp="test/fixture/survey_point.shp",
            foodchain_info_csv="test/fixture/foodchain_info.csv"
        )
        cls.bt.run_f5()

        cls.wgs = cls.temp_result_dir / "process/biotope3_WGS.shp"
        cls.shp = cls.temp_result_dir / "result_f5/biotope3_WGS_f5.shp"
        cls.csv = cls.temp_result_dir / "result_f5/biotope3_WGS_f5.csv"

    def test_wgs_exists(self):
        self.assertTrue(self.wgs.exists)

    def test_wgs_correct(self):
        result = arcutils.shp_to_df(self.wgs)
        answer = arcutils.shp_to_df("test/answer/process3/biotope3_WGS.shp")
        self.assertTrue(result.equals(answer))

    def test_shp_exists(self):
        self.assertTrue(self.shp.exists())

    def test_shp_correct(self):
        result = arcutils.shp_to_df(self.shp)
        answer = arcutils.shp_to_df("test/answer/result_f5/biotope3_WGS_f5.shp")
        self.assertTrue(result.equals(answer))

    def test_csv_exists(self):
        self.assertTrue(self.csv.exists())

    def test_csv_correct(self):
        result = pd.read_csv(self.csv)
        answer = pd.read_csv("test/answer/result_f5/biotope3_WGS_f5.csv")
        self.assertTrue(result.equals(answer))

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.temp_result_dir)
