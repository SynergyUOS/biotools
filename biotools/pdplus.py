import pandas as pd


def left_merge_with_default(left_df: pd.DataFrame, right_df: pd.DataFrame, on, default):
    result_df = pd.merge(left_df, right_df, on=on, how="left")
    result_df = result_df.fillna({field: default for field in right_df.columns})
    return result_df
