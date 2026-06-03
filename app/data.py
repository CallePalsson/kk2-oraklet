from io import BytesIO

import pandas as pd


_dataframe = pd.DataFrame()


def save_csv(content: bytes) -> pd.DataFrame:
    global _dataframe

    df = pd.read_csv(BytesIO(content))
    if df.empty:
        raise ValueError("CSV file does not contain any rows")

    _dataframe = df
    return _dataframe


def get_dataframe() -> pd.DataFrame:
    return _dataframe


def clear_data() -> None:
    global _dataframe
    _dataframe = pd.DataFrame()


def get_stats() -> dict:
    return _dataframe.describe(include="all").fillna("").to_dict()
