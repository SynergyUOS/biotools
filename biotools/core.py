from os import PathLike
from pathlib import Path
from typing import Sequence, Union

import arcpy.management as am

from biotools import arcutils, habitat, foodchain


class Biotools:

    def __init__(
        self,
        biotope_shp: Union[str, PathLike],
        result_directory: Union[str, PathLike],
        environmentallayer_directory: Union[str, PathLike] = None,
        keystone_species_csv: Union[str, PathLike] = None,
        commercialarea_csv: Union[str, PathLike] = None,
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
            `keystonespecies_csv`
                Used at H4, H6.
            `commercialarea_csv`
                Used at H5.
            `surveypoint_shp`
                Used at F1, F2, F3, F4, F5, F6
            `foodchaininfo_csv`
                Used at F1, F2, F3, F4, F5
        """
        self._base_dir = Path(result_directory)
        self._process_dir = self._base_dir / "process"
        self._process_dir.mkdir(parents=True, exist_ok=True)
        self._biotope_wgs_shp = self._prepare_shp(biotope_shp, "BT_ID")

        if environmentallayer_directory is not None:
            self._environmentallayer_dir = Path(environmentallayer_directory)
        if keystone_species_csv is not None:
            self._keystonespecies_csv = keystone_species_csv
        if commercialarea_csv is not None:
            self._commercialarea_csv = commercialarea_csv
        if surveypoint_shp is not None:
            self._surveypoint_wgs_shp = self._prepare_shp(surveypoint_shp, "SP_ID")
        if foodchain_info_csv is not None:
            self._foodchaininfo_csv = foodchain_info_csv

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

    def _create_result_shp(self, tag):
        result = self._base_dir / f"result_{tag}" / (self._biotope_wgs_shp.stem + f"_{tag}.shp")
        result.parent.mkdir(parents=True, exist_ok=True)
        return result

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
        self,
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

    def evaluate_leastcost_distribution(
        self,
    ):
        pass

    def evaluate_pieceofland_occurrence(
        self,
    ):
        pass

    def evaluate_pieceofland_availability(
        self,
    ):
        pass

    def evaluate_foodresource_count(
        self,
    ):
        pass

    def evaluate_diversity_index(
        self,
    ):
        pass

    def evaluate_combinable_producers_and_consumers(
        self,
    ):
        pass

    def evaluate_connection_strength(
        self,
    ):
        pass

    def evaluate_similar_functional_species(
        self,
    ):
        pass

    def evaluate_foodresource_inhabitation(
        self,
    ):
        pass

    run_h1 = evaluate_habitat_size
    run_h2 = evaluate_structured_layer
    run_h3 = evaluate_patch_isolation
    run_h4 = evaluate_leastcost_distribution
    run_h5 = evaluate_pieceofland_occurrence
    run_h6 = evaluate_pieceofland_availability

    run_f1 = evaluate_foodresource_count
    run_f2 = evaluate_diversity_index
    run_f3 = evaluate_combinable_producers_and_consumers
    run_f4 = evaluate_connection_strength
    run_f5 = evaluate_similar_functional_species
    run_f6 = evaluate_foodresource_inhabitation
