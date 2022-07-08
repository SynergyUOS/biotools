from typing import Callable

import pandas as pd


def drop_if(
    df: pd.DataFrame,
    condition: Callable[[pd.DataFrame], pd.Series]
) -> pd.DataFrame:
    return df.drop(df[condition(df)].index)


def replace_row(
    df: pd.DataFrame,
    mapper: dict,
    condition: Callable[[pd.DataFrame], pd.Series]
) -> pd.DataFrame:
    result_df = df.copy()
    result_df.loc[condition(df), mapper.keys()] = mapper.values()
    return result_df
