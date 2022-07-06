import importlib.resources
from os import PathLike
from pathlib import Path
import subprocess

import pandas as pd


def run_maxent(samplesfile: PathLike,
               environmentallayers: PathLike,
               outputdirectory: PathLike,
               overrite: bool = False,
               **kwargs):
    """
    Args:
        `samplesfile`: PathLike
            Path to table which contians species occurrence information (.csv).
        `environmentallayers`: PathLike
            Path to directory which contains environmant variable maps (.asc).
        `outputdirectory`: PathLike
            Path to directory to which maxent saves results.

        Options of basicRun:
            `skipifexists`: boolean, default `True`
            `autorun`: boolean, default `True`
            `autofeature`: boolean, default `True`
            `responsecurves`: boolean, default `True`
            `jackknife`: boolean, default `True`
            `visible`: boolean, default `False`
            `warnings`: boolean, default `False`

        Options of advancdRun:
            `writeplotdata`: boolean, default `False`
            `appendtoresultsfile`: boolean, default `False`
                결과파일(maxentResults.csv) 초기화(F) or 추가(T)
            `writebackgroundpredictions`: boolean, default `False`
    """
    kwargs.setdefault("skipifexists", True)
    # kwargs.setdefault("askoverwrite", False)
    kwargs.setdefault("autorun", True)
    kwargs.setdefault("autofeature", True)
    kwargs.setdefault("responsecurves", True)
    kwargs.setdefault("jackknife", True)
    kwargs.setdefault("visible", False)
    kwargs.setdefault("warnings", False)
    kwargs.setdefault("writeplotdata", False)
    kwargs.setdefault("appendtoresultsfile", True)
    kwargs.setdefault("writebackgroundpredictions", False)

    Path(outputdirectory).mkdir(parents=True, exist_ok=True)

    with importlib.resources.path("biotools.lib", "maxent.jar") as path:
        command = [
            "java", "-mx512m", "-jar", path,
            f"samplesfile={samplesfile}",
            f"environmentallayers={environmentallayers}",
            f"outputdirectory={outputdirectory}",
        ]
        command += kwargs_to_command(kwargs)

    subprocess.run(command)

    output_dir = Path(outputdirectory)
    summary_df = pd.read_csv(output_dir / "maxentResults.csv", encoding="euc-kr")
    name_s = summary_df["Species"]
    return [output_dir / f"{name}.asc" for name in name_s]



def kwargs_to_command(kwargs):
    return [f"{param}={arg}" for param, arg in kwargs.items()]


# ascs = run_maxent(
#     environmentallayers="D:/dev/uos/biotools/input/env",
#     samplesfile="D:/dev/uos/biotools/input/기존_수원_까마귀.csv",
#     outputdirectory="D:/dev/uos/biotools/output/maxent",
# )

# print(ascs)