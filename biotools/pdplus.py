from typing import Callable, Sequence

import pandas as pd


def left_merge_with_default(left_df: pd.DataFrame, right_df: pd.DataFrame, on, default):
    result_df = pd.merge(left_df, right_df, on=on, how="left")
    result_df = result_df.fillna({field: default for field in right_df.columns})
    return result_df


def drop_if(
    df: pd.DataFrame,
    condition: Callable[[pd.DataFrame],
    pd.Series]
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
