from os import PathLike
from pathlib import Path
from typing import Sequence, Union

import arcpy.management as am
import pandas as pd

from biotools import arcutils, habitat, foodchain


class Biotools:

    def __init__(
        self,
        biotope_shp: Union[str, PathLike],
        result_directory: Union[str, PathLike],
        environmentallayer_directory: Union[str, PathLike] = None,
        keystone_species_csv: Union[str, PathLike] = None,
        commercialpoint_csv: Union[str, PathLike] = None,
        surveypoint_shp: Union[str, PathLike] = None,
        foodchain_info_csv: Union[str, PathLike] = None
    ):
        """
        Args:
            `biotope_shp`
                Must have biotope code field.
            `result_directory`
                Recommend to use empty directory.
            `environmentallayer_directory`
                Used at H4, H6, F6.
            `keystone_species_csv`
                Used at H4, H6.
            `commercialpoint_csv`
                Used at H5.
            `surveypoint_shp`
                Used at F1, F2, F3, F4, F5, F6
            `foodchain_info_csv`
                Used at F1, F2, F3, F4, F5
        """
        self._base_dir = Path(result_directory).absolute()
        self._process_dir = self._base_dir / "process"
        self._process_dir.mkdir(parents=True, exist_ok=True)
        self._biotope_wgs_shp = self._prepare_shp(biotope_shp, "BT_ID")

        if environmentallayer_directory is not None:
            self._environmentallayer_dir = Path(environmentallayer_directory).absolute()
        if keystone_species_csv is not None:
            self._keystone_species_csv = Path(keystone_species_csv).absolute()
        if commercialpoint_csv is not None:
            self._commercialpoint_csv = Path(commercialpoint_csv).absolute()
        if surveypoint_shp is not None:
            self._surveypoint_wgs_shp = self._prepare_shp(surveypoint_shp, "SP_ID")
        if foodchain_info_csv is not None:
            self._foodchain_info_csv = Path(foodchain_info_csv).absolute()

    def _prepare_shp(self, shp, newidfield):
        newshp = self._process_dir / (Path(shp).stem + "_WGS.shp")
        if not newshp.exists():
            am.Project(str(shp), str(newshp), arcutils.WGS1984_PRJ)
        if newidfield not in arcutils.get_fields(newshp):       # create unique field
            am.CalculateField(
                str(newshp),
                newidfield,
                f"'{newidfield}!FID!'",
                expression_type="PYTHON3",
                field_type="TEXT"
            )
        return newshp

    def _create_result_shp(self, tag):
        result = self._base_dir / f"result_{tag}" / (self._biotope_wgs_shp.stem + f"_{tag}.shp")
        result.parent.mkdir(parents=True, exist_ok=True)
        return result

    def _create_maxent_dir(self, stem):
        result = self._process_dir / (stem + "_maxent")
        result.mkdir(parents=True, exist_ok=True)
        return result

    def evaluate_habitat_size(
        self,
        lower_bounds: Sequence[float] = (50, 10, 1, 0),
        scores: Sequence[float] = (1, 0.5, 0.3, 0.2)
    ) -> str:
        """Evaluate habitat size.

        Return:
            Path to result file(shp).
        """
        result_shp = self._create_result_shp("h1")
        sized_shp = self._process_dir / (self._biotope_wgs_shp.stem + "_sized.shp")
        h1 = habitat.HabitatSize(
            self._biotope_wgs_shp,
            result_shp,
            sized_shp,
            lower_bounds,
            scores
        )
        return h1.run()

    def evaluate_structured_layer(
        self,
        scores: Sequence[float] = (0.3, 0.6, 1)
    ) -> str:
        """Evaluate structured layer.

        Return:
            Path to result file(shp).
        """
        result_shp = self._create_result_shp("h2")
        h2 = habitat.StructuredLayer(
            self._biotope_wgs_shp,
            result_shp,
            scores
        )
        return h2.run()

    def evaluate_patch_isolation(
        self
    ):
        """Evaluate patch isolation.

        Return:
            Path to result file(shp).
        """
        result_shp = self._create_result_shp("h3")
        h3 = habitat.PatchIsolation(
            self._biotope_wgs_shp,
            result_shp,
        )
        return h3.run()

    def evaluate_least_cost_distribution(
        self
    ):
        """Evaluate least cost distribution.

        Return:
            Path to result file(shp).
        """
        maxent_dir = self._create_maxent_dir(self._keystone_species_csv.stem)
        result_shp = self._create_result_shp("h4")
        h4 = habitat.LeastCostDistribution(
            self._biotope_wgs_shp,
            self._keystone_species_csv,
            self._environmentallayer_dir,
            maxent_dir,
            result_shp,
        )
        return h4.run()

    def evaluate_pieceofland_occurrence(
        self,
        cellsize: float = 5
    ):
        """Evaluate occurrence probability of piece of land.

        Args:
            `cellsize`: `float`, default 5.
                Cellsize should be less than the smallest biotope. If a biotope is too small
                to contain a cell, ZonalStatistics will skip the biotope.

        Return:
            Path to result file(shp).
        """
        result_shp = self._create_result_shp("h5")
        h5 = habitat.PieceoflandOccurrence(
            self._biotope_wgs_shp,
            self._commercialpoint_csv,
            result_shp,
            cellsize
        )
        return h5.run()

    def evaluate_pieceofland_availability(
        self,
        threshold: float = 0.5,
        cellsize: float = 5
    ):
        """Evaluate Availability of Piece of Land.

        Return:
            Path to result file(shp).
        """
        maxent_dir = self._create_maxent_dir(self._keystone_species_csv.stem)
        result_shp = self._create_result_shp("h6")
        h6 = habitat.PieceoflandAvailability(
            self._biotope_wgs_shp,
            self._keystone_species_csv,
            self._environmentallayer_dir,
            maxent_dir,
            result_shp,
            threshold,
            cellsize
        )
        return h6.run()

    def evaluate_food_resource_count(
        self,
        skip_noname: bool = True
    ):
        """Evaluate the number of food resources.

        Return:
            Path to result file(shp).
        """
        result_shp = self._create_result_shp("f1")
        f1 = foodchain.FoodResourceCount(
            self._biotope_wgs_shp,
            self._surveypoint_wgs_shp,
            self._foodchain_info_csv,
            result_shp,
            skip_noname
        )
        return f1.run()

    def evaluate_diversity_index(
        self,
        skip_noname: bool = True
    ):
        """Evaluate Shannon diversity index.

        Return:
            Path to result file(shp).
        """
        result_shp = self._create_result_shp("f2")
        f2 = foodchain.DiversityIndex(
            self._biotope_wgs_shp,
            self._surveypoint_wgs_shp,
            self._foodchain_info_csv,
            result_shp,
            skip_noname
        )
        return f2.run()

    def evaluate_combinable_producers_and_consumers(
        self,
        skip_noname: bool = True,
        scores: Sequence[float] = (1, 0.6, 0.3),
    ):
        """Evaluate combinable producers and consumers.

        Return:
            Path to result file(shp).
        """
        result_shp = self._create_result_shp("f3")
        f3 = foodchain.CombinableProducersAndConsumers(
            self._biotope_wgs_shp,
            self._surveypoint_wgs_shp,
            self._foodchain_info_csv,
            result_shp,
            skip_noname,
            scores
        )
        return f3.run()

    def evaluate_connection_strength(
        self,
        skip_noname: bool = True
    ):
        """Evaluate connection strength

        Return:
            Path to result file(shp).
        """
        result_shp = self._create_result_shp("f4")
        f4 = foodchain.ConnectionStrength(
            self._biotope_wgs_shp,
            self._surveypoint_wgs_shp,
            self._foodchain_info_csv,
            result_shp,
            skip_noname
        )
        return f4.run()

    def evaluate_similar_functional_species(
        self,
        skip_noname: bool = True
    ):
        """Evaluate similar functional species.

        Return:
            Path to result file(shp).
        """
        result_shp = self._create_result_shp("f5")
        f5 = foodchain.SimilarFunctionalSpecies(
            self._biotope_wgs_shp,
            self._surveypoint_wgs_shp,
            self._foodchain_info_csv,
            result_shp,
            skip_noname
        )
        return f5.run()

    def evaluate_food_resource_inhabitation(
        self,
    ):
        newstem = self._surveypoint_wgs_shp.stem.replace("WGS", "ITRF")
        surveypoint_itrf_shp = self._surveypoint_wgs_shp.with_stem(newstem)
        if not surveypoint_itrf_shp.exists():
            am.Project(
                str(self._surveypoint_wgs_shp),
                str(surveypoint_itrf_shp),
                arcutils.ITRF2000_PRJ
            )

        maxent_dir = self._create_maxent_dir("prey")
        result_shp = self._create_result_shp("f6")
        sample_csv = self._process_dir / "prey_sample.csv"
        f6 = foodchain.FoodResourceInhabitation(
            self._biotope_wgs_shp,
            self._environmentallayer_dir,
            surveypoint_itrf_shp,
            self._foodchain_info_csv,
            sample_csv,
            maxent_dir,
            result_shp,
        )
        return f6.run()

    def merge(self):
        result_df = arcutils.shp_to_df(self._biotope_wgs_shp)[["BT_ID"]]
        habitats = sorted(self._base_dir.glob("result_h[1-6]/*.csv"))
        foodchains = sorted(self._base_dir.glob("result_f[1-6]/*.csv"))
        for path in habitats + foodchains:
            df = pd.read_csv(path)
            result_df = result_df.merge(df, how="left", on="BT_ID")

        result_path = self._create_result_shp("full")
        return arcutils.clean_join(self._biotope_wgs_shp, result_df, result_path)

    # aliasing
    run_h1 = evaluate_habitat_size
    run_h2 = evaluate_structured_layer
    run_h3 = evaluate_patch_isolation
    run_h4 = evaluate_least_cost_distribution
    run_h5 = evaluate_pieceofland_occurrence
    run_h6 = evaluate_pieceofland_availability

    run_f1 = evaluate_food_resource_count
    run_f2 = evaluate_diversity_index
    run_f3 = evaluate_combinable_producers_and_consumers
    run_f4 = evaluate_connection_strength
    run_f5 = evaluate_similar_functional_species
    run_f6 = evaluate_food_resource_inhabitation
