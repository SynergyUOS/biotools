import math

import arcpy
import arcpy.analysis as aa
import arcpy.management as am
import arcpy.sa as asa
import pandas as pd

from biotools import arcutils, maxent, pdplus


class FoodResourceCount:

    def __init__(
        self,
        biotope_shp,
        surveypoint_shp,
        foodchin_info_csv,
        result_shp,
        skip_noname=True
    ):
        self._biotope_shp = str(biotope_shp)
        self._surveypoint_shp = str(surveypoint_shp)
        self._foodchain_info_df = pd.read_csv(foodchin_info_csv, encoding="euc-kr")
        self._result_shp = str(result_shp)
        self._skip_noname = skip_noname
        self._surverpoint = _Surveypoint(
            self._surveypoint_shp,
            self._biotope_shp,
            self._foodchain_info_df
        )

    def run(self):
        self._surverpoint.enrich(self._skip_noname)
        surveypoint_df = self._surverpoint.df

        table = []
        for bt_id, sub_df in surveypoint_df.groupby("BT_ID"):
            if bt_id is None:
                continue
            count_s = sub_df.groupby("Owls_foods").sum()["개체수"]
            total_count = count_s.sum()
            prey_count = count_s.get("Prey_S", 0)
            result = prey_count / total_count
            table.append([bt_id, prey_count, total_count, result])

        result_df = pd.DataFrame(
            table,
            columns=["BT_ID", "F1_PREY_N", "F1_TOTAL_N", "F1_RESULT"]
        )
        biotope_df = arcutils.shp_to_df(self._biotope_shp)
        result_df = biotope_df[["BT_ID"]].merge(result_df, how="left", on="BT_ID")
        result_df = result_df.fillna({"F1_RESULT": 0})
        return arcutils.clean_join(self._biotope_shp, result_df, self._result_shp)


class DiversityIndex:

    def __init__(
        self,
        biotope_shp,
        surveypoint_shp,
        foodchain_info_csv,
        result_shp,
        skip_noname=True
    ):
        self._biotope_shp = str(biotope_shp)
        self._surveypoint_shp = str(surveypoint_shp)
        self._foodchain_info_df = pd.read_csv(foodchain_info_csv, encoding="euc-kr")
        self._result_shp = str(result_shp)
        self._skip_noname = skip_noname
        self._surverpoint = _Surveypoint(
            self._surveypoint_shp,
            self._biotope_shp,
            self._foodchain_info_df
        )

    def run(self):
        self._surverpoint.enrich(self._skip_noname)
        surveypoint_df = self._surverpoint.df

        table = []
        for bt_id, sub_df in surveypoint_df.groupby("BT_ID"):
            if bt_id is None:
                continue
            count_s = sub_df.groupby("국명").sum()["개체수"]
            shannon_index = self._get_shannon_index(count_s)
            table.append([bt_id, count_s.sum(), shannon_index])

        result_df = pd.DataFrame(table, columns=["BT_ID", "F2_PREY_N", "F2_SHANNON"])
        result_df = result_df.assign(
            F2_RESULT=lambda x: self._minmax_normalize(x["F2_SHANNON"])
        )
        biotope_df = arcutils.shp_to_df(self._biotope_shp)
        result_df = biotope_df[["BT_ID"]].merge(result_df, how="left", on="BT_ID")
        result_df = result_df.fillna({"F2_RESULT": 0})
        return arcutils.clean_join(self._biotope_shp, result_df, self._result_shp)

    def _get_shannon_index(self, counts):
        total = sum(counts)
        proportions = [count / total for count in counts]
        return sum(-(p * math.log2(p)) for p in proportions)

    def _minmax_normalize(self, seq):
        maximum = max(seq)
        minimum = min(seq)
        return [(i - minimum) / (maximum - minimum) for i in seq]


class CombinableProducersAndConsumers:

    def __init__(
        self,
        biotope_shp,
        surveypoint_shp,
        foodchain_info_csv,
        result_shp,
        skip_noname=True,
        scores=(0.3, 0.6, 1)
    ):
        self._biotope_shp = str(biotope_shp)
        self._surveypoint_shp = str(surveypoint_shp)
        self._foodchain_info_df = pd.read_csv(foodchain_info_csv, encoding="euc-kr")
        self._result_shp = str(result_shp)
        self._skip_noname = skip_noname
        self._scores = scores
        self._surverpoint = _Surveypoint(
            self._surveypoint_shp,
            self._biotope_shp,
            self._foodchain_info_df
        )

    def run(self):
        self._surverpoint.enrich(self._skip_noname)
        surveypoint_df = self._surverpoint.df

        table = []
        for bt_id, sub_df in surveypoint_df.groupby("BT_ID"):
            if bt_id is None:
                continue
            count_s = sub_df["D_Level"].value_counts()
            d_counts = [count_s.get(d_name, 0) for d_name in ["D1", "D2", "D3"]]
            unique_count = sum(bool(d_count) for d_count in d_counts)
            score = self._scores[unique_count - 1]
            table.append([bt_id, *d_counts, score])

        result_df = pd.DataFrame(
            table,
            columns=["BT_ID", "F3_D1_N", "F3_D2_N", "F3_D3_N", "F3_RESULT"]
        )
        biotope_df = arcutils.shp_to_df(self._biotope_shp)
        result_df = biotope_df[["BT_ID"]].merge(result_df, how="left", on="BT_ID")
        result_df = result_df.fillna({"F3_RESULT": 0})
        return arcutils.clean_join(self._biotope_shp, result_df, self._result_shp)


class ConnectionStrength:

    def __init__(
        self,
        biotope_shp,
        surveypoint_shp,
        foodchain_info_csv,
        result_shp,
        skip_noname=True,
    ):
        self._biotope_shp = str(biotope_shp)
        self._surveypoint_shp = str(surveypoint_shp)
        self._foodchain_info_df = pd.read_csv(foodchain_info_csv, encoding="euc-kr")
        self._result_shp = str(result_shp)
        self._skip_noname = skip_noname
        self._surverpoint = _Surveypoint(
            self._surveypoint_shp,
            self._biotope_shp,
            self._foodchain_info_df
        )

    def run(self):
        self._surverpoint.enrich(self._skip_noname)
        surveypoint_df = self._surverpoint.df

        table = []
        for bt_id, sub_df in surveypoint_df.groupby("BT_ID"):
            if bt_id is None:
                continue
            count_s = sub_df["Owls_foods"].value_counts()
            prey_count = count_s.get("Prey_S", 0)
            table.append([bt_id, prey_count, int(prey_count > 0)])

        result_df = pd.DataFrame(table, columns=["BT_ID", "F4_PREY_N", "F4_RESULT"])
        biotope_df = arcutils.shp_to_df(self._biotope_shp)
        result_df = biotope_df[["BT_ID"]].merge(result_df, how="left", on="BT_ID")
        result_df = result_df.fillna({"F4_RESULT": 0})
        return arcutils.clean_join(self._biotope_shp, result_df, self._result_shp)


class SimilarFunctionalSpecies:

    def __init__(
        self,
        biotope_shp,
        surveypoint_shp,
        foodchain_info_csv,
        result_shp,
        skip_noname=True,
    ):
        self._biotope_shp = str(biotope_shp)
        self._surveypoint_shp = str(surveypoint_shp)
        self._foodchain_info_df = pd.read_csv(foodchain_info_csv, encoding="euc-kr")
        self._result_shp = str(result_shp)
        self._skip_noname = skip_noname
        self._surverpoint = _Surveypoint(
            self._surveypoint_shp,
            self._biotope_shp,
            self._foodchain_info_df
        )

    def run(self):
        self._surverpoint.enrich(self._skip_noname)
        surveypoint_df = self._surverpoint.df

        table = []
        for bt_id, sub_df in surveypoint_df.groupby("BT_ID"):
            if bt_id is None:
                continue
            count_s = sub_df["Alternative_S"].value_counts()
            threatened_count = count_s.get("Threatened_S", 0)
            alt_alien_count = count_s.get("Alt_Alien_S", 0)
            alt_count = count_s.get("Alt_S", 0)
            normal_count = count_s.get("Normal_S", 0)
            table.append([
                bt_id,
                threatened_count,
                alt_alien_count,
                alt_count,
                normal_count,
                self._score_orderly([alt_count, alt_alien_count], [1, 0.5], 0),
            ])

        result_df = pd.DataFrame(
            table,
            columns=["BT_ID", "F5_THRT_N", "F5_ALIEN_N", "F5_ALT_N", "F5_NORM_N", "F5_RESULT"]
        )
        biotope_df = arcutils.shp_to_df(self._biotope_shp)
        result_df = biotope_df[["BT_ID"]].merge(result_df, how="left", on="BT_ID")
        result_df = result_df.fillna({"F5_RESULT": 0})
        return arcutils.clean_join(self._biotope_shp, result_df, self._result_shp)

    def _score_orderly(self, counts, scores, default):
        for count, score in zip(counts, scores):
            if count > 0:
                return score
        return default


class FoodResourceInhabitation:

    def __init__(
        self,
        biotope_shp,
        environmentallayer_dir,
        surveypoint_shp,
        foodchain_info_csv,
        sample_csv,
        maxent_dir,
        result_shp,
    ):
        self._biotope_shp = str(biotope_shp)
        self._environmentallayer_dir = str(environmentallayer_dir)
        self._surveypoint_shp = str(surveypoint_shp)
        self._foodchain_info_df = pd.read_csv(foodchain_info_csv, encoding="euc-kr")
        self._sample_csv = str(sample_csv)
        self._maxent_dir = str(maxent_dir)
        self._result_shp = str(result_shp)
        self._surverpoint = _Surveypoint(
            self._surveypoint_shp,
            None,
            self._foodchain_info_df
        )

    def run(self):
        self._surverpoint.merge()
        surveypoint_itrf_df = self._surverpoint.df
        self._export_samples(surveypoint_itrf_df, self._sample_csv)

        ascs = maxent.run_maxent(
            self._sample_csv,
            self._environmentallayer_dir,
            self._maxent_dir,
        )

        mean_raster = asa.CellStatistics([str(asc) for asc in ascs], "MEAN")
        with arcpy.EnvManager(outputCoordinateSystem=arcutils.ITRF2000_PRJ):
            result_table = asa.ZonalStatisticsAsTable(
                self._biotope_shp,
                "BT_ID",
                mean_raster,
                "memory/result_table",
                statistics_type="MEAN"
            )
        result_df = arcutils.shp_to_df(result_table)
        am.Delete(result_table)

        result_df = result_df.drop(columns="ZONE_CODE")
        result_df = result_df.rename(columns={
            "COUNT": "F6_COUNT",
            "AREA": "F6_AREA",
            "MEAN": "F6_RESULT",
        })
        biotope_df = arcutils.shp_to_df(self._biotope_shp)
        result_df = biotope_df[["BT_ID"]].merge(result_df, how="left", on="BT_ID")
        result_df = result_df.fillna({"F6_RESULT": 0})
        return arcutils.clean_join(self._biotope_shp, result_df, self._result_shp)

    def _export_samples(self, df, path):
        df = df[df["Owls_foods"] == "Prey_S"]
        df = df[["국명", "Shape"]]
        df = df.assign(
            LONGITUDE=lambda x: x["Shape"].apply(lambda x: x[0]),
            LATITUDE=lambda x: x["Shape"].apply(lambda x: x[1]),
        )
        df = df.drop(columns="Shape")
        df.to_csv(path, index=False, encoding="euc-kr")


class _Surveypoint:

    def __init__(self, surveypoint_shp, biotope_shp, foodchain_info_df):
        self._biotope_shp = str(biotope_shp)
        self._surveypoint_shp = str(surveypoint_shp)
        self._foodchain_info_df = foodchain_info_df
        self._surverpoint_df = arcutils.shp_to_df(surveypoint_shp)

    @property
    def df(self):
        return self._surverpoint_df

    def enrich(self, skip_noname=True):
        joined = aa.SpatialJoin(self._surveypoint_shp, self._biotope_shp, "memory/joined")
        self._surverpoint_df = arcutils.shp_to_df(joined)
        am.Delete(joined)

        self.merge(skip_noname)

        self._surverpoint_df["개체수"] = pd.to_numeric(
            self._surverpoint_df["개체수"],
            errors="coerce"
        ).fillna(1)

    def merge(self, skip_noname=True):
        self._surverpoint_df = pd.merge(
            self._surverpoint_df,
            self._foodchain_info_df,
            how="left",
            left_on="국명",
            right_on="S_Name"
        )

        if skip_noname:
            self._surverpoint_df = pdplus.drop_if(
                self._surverpoint_df,
                lambda x: x["국명"] == " "
            )
        else:
            self._surverpoint_df = pdplus.replace_row(
                self._surverpoint_df,
                {
                    "국명": "Noname",
                    "Owls_foods": "Normal_S",
                    "D_Level": "D3",
                    "Alternative_s": "Normal_S"
                },
                lambda x: x["국명"] == " "
            )
