from os import PathLike
from pathlib import Path
from typing import Sequence, Union

import arcpy.management as am
import pandas as pd

from biotools import arcutils, habitat, foodchain


class Biotools:
    """Biotope Evaluation Toolset Using Arcpy and Maxent.

    Creates a process directory in `result_directory`.

    Args:
        `biotope_shp`: Path to biotope shapefile.
        `result_directory`: Path to directory to which results save. Empty
            directory is recommended for different inputs.
        `environmentallayer_directory`: Path to directory which contains
            environmental layers for maxent. It is used at H4, H6, F6.
        `keystone_species_csv`: Path to keystone species point csv file. It is
            used at H4, H6.
        `commercialpoint_csv`: Path to commercial area point csv file. It is
            used at H5.
        `surveypoint_shp`: Path to survey point shapefile. It is used at F1,
            F2, F3, F4, F5, F6.
        `foodchain_info_csv`: Path to foodchain information csv file. It is
            used at F1, F2, F3, F4, F5.
    """

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
        """Evaluates habitat size.

        Creates result_h1 directory in the result directory, and saves result shapefile in it.

        Args:
            `lower_bounds`, `scores`: If `lower_bounds[n]` <= area < `lower_bounds[n - 1]`,
                `scores[n]` will be taken for the area. The lengths of `lower_bounds`
                and `scores` must be the same.

        Returns:
            Path to result shapefile.
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
        """Evaluates structured layer.

        Creates result_h2 directory in the result directory, and saves result shapefile in it.

        Args:
            `scores`: `scores[0]` for 1 storey strcutrue. `socres[1]` for 2 storey
                structure. `scores[2]` for 3 storey structure.

        Returns:
            Path to result shapefile.
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
        """Evaluates patch isolation.

        Creates result_h3 directory in the result directory, and saves result shapefile in it.

        Args:
            [to do] buffer_size?

        Returns:
            Path to result shapefile.
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
        """Evaluates least cost distribution.

        Creates result_h4 directory in the result directory, creates a maxent directory
        containing maxent results in process directory, and saves final result shapefile in result_h4.

        Returns:
            Path to result shapefile.
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
        """Evaluates occurrence probability of piece of land.

        Creates result_h5 directory in the result directory, and saves result shapefile in it.

        Args:
            `cellsize`: Cell size used for `EucDistance`. It should be less than
                the smallest biotope. If a biotope is too small to contain a cell,
                `ZonalStatisticsAsTable` will skip the biotope.

        Returns:
            Path to result shapefile.
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
        """Evaluate availability of piece of land.

        Creates result_h6 directory in the result directory, creates a maxent directory
        containing maxent results in process directory, and saves final result shapefile in result_h6.

        Args:
            `threshold`: Probability threshold for defining major habitat.
            `cellsize`: Cell size used for `EucDistance`. It should be less than
                the smallest biotope. If a biotope is too small to contain a cell,
                `ZonalStatisticsAsTable` will skip the biotope.

        Returns:
            Path to result shapefile.
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

        Creates result_f1 directory in result directory, and saves result shapefile in it.

        Args:
            `skip_noname`: If it is `True`, records for which '국명' is not defined
                will be skipped. If `False`, they will take `["Normal_S", "D3", "Normal_S"]`
                as foodchain information.

        Returns:
            Path to result shapefile.
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

        Creates result_f2 directory in result directory, and saves result shapefile in it.

        Args:
            `skip_noname`: If it is `True`, records for which '국명' is not defined
                will be skipped. If `False`, they will take `["Normal_S", "D3", "Normal_S"]`
                as foodchain information.

        Returns:
            Path to result shapefile.
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
        scores: Sequence[float] = (0.3, 0.6, 1),
    ):
        """Evaluate combinable producers and consumers.

        Creates result_f3 directory in result directory, and saves result shapefile in it.

        Args:
            `skip_noname`: If it is `True`, records for which '국명' is not defined
                will be skipped. If `False`, they will take `["Normal_S", "D3", "Normal_S"]`
                as foodchain information.
            `scores`: scores[0] for primary consumers, scores[1] for secondary consumers,
                and scores[2] for tertiary consumers.

        Returns:
            Path to result shapefile.
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

        Creates result_f4 directory in result directory, and saves result shapefile in it.

        Args:
            `skip_noname`: If it is `True`, records for which '국명' is not defined
                will be skipped. If `False`, they will take `["Normal_S", "D3", "Normal_S"]`
                as foodchain information.

        Returns:
            Path to result shapefile.
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
        """Evaluates similar functional species.

        Creates result_f5 directory in result directory, and saves result shapefile in it.

        Args:
            `skip_noname`: If it is `True`, records for which '국명' is not defined
                will be skipped. If `False`, they will take `["Normal_S", "D3", "Normal_S"]`
                as foodchain information.

        Returns:
            Path to result shapefile.
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
        """Evaluates inhabitation of food resources.

        Creates result_f6 directory in result directory, creates a maxent directory
        containing maxent results in process directory, and saves final result shapefile in result_f6.

        Returns:
            Path to result shapefile.
        """
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
        """Merges each result to one file.

        Returns:
            Path to merged result shapefile.
        """
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
