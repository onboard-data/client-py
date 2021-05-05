import pandas as pd
from typing import Iterable, Dict, List, Union
from onboard.client.models import PointData


def points_df_from_timeseries(timeseries, points=[]) -> pd.DataFrame:
    """Returns a pandas dataframe from the results of a timeseries query"""

    # 'type' is from the point_type.display_name column
    point_names = {str(p['id']): p.get('type') for p in points}

    columns = ['timestamp']
    dates = set()
    data_by_point = {}

    for point in timeseries:
        point_id = point['tags']['point_id']
        columns.append(point_id)
        col_indexes = point['columns']

        ts_index = col_indexes.index('time')
        clean_index = col_indexes.index('clean')

        point_data: Dict[str, float] = {}
        data_by_point[point_id] = point_data

        for val in point['values']:
            ts = val[ts_index]
            dates.add(ts)
            clean = val[clean_index]
            point_data[ts] = clean

    sorted_dates = list(dates)
    sorted_dates.sort()
    data = []

    for d in sorted_dates:
        row = {'timestamp': d}
        for p in columns[1:]:
            val = data_by_point[p].get(d)
            point_name = point_names.get(p)
            point_col = f"{point_name} - {p}" if point_name else p
            row[point_col] = val
        data.append(row)

    df = pd.DataFrame(data)
    return df


def points_df_from_streaming_timeseries(timeseries: Iterable[PointData],
                                        points=[],
                                        point_column_label=None,
                                        ) -> pd.DataFrame:
    """Returns a pandas dataframe from the results of a timeseries query"""
    if point_column_label is None:
        def point_column_label(p):
            return p.get('id')

    point_names = {p['id']: point_column_label(p) for p in points}
    columns: List[Union[str, int]] = ['timestamp']
    dates = set()
    data_by_point = {}

    for point in timeseries:
        columns.append(point.point_id)
        ts_index = point.columns.index('time')
        data_index = point.columns.index(point.unit)

        point_data: Dict[str, Union[str, float, None]] = {}
        data_by_point[point.point_id] = point_data

        for val in point.values:
            ts: str = val[ts_index]  # type: ignore[assignment]
            dates.add(ts)
            clean = val[data_index]
            point_data[ts] = clean

    sorted_dates = list(dates)
    sorted_dates.sort()
    data = []

    for d in sorted_dates:
        row = {'timestamp': d}
        for p in columns[1:]:
            val = data_by_point[p].get(d)  # type: ignore
            point_col = point_names.get(p, p)
            row[point_col] = val  # type: ignore
        data.append(row)

    df = pd.DataFrame(data)
    return df


def df_time_index(df: pd.DataFrame,
                  time_col='timestamp', utc=True) -> pd.DataFrame:
    dt_series = pd.to_datetime(df[time_col], infer_datetime_format=True)
    datetime_index = pd.DatetimeIndex(dt_series.values)
    if utc:
        datetime_index = datetime_index.tz_localize('UTC')
    df_indexed = df.set_index(datetime_index)
    df_indexed.drop(time_col, axis=1, inplace=True)
    return df_indexed


def df_objs_to_numeric(df: pd.DataFrame):
    cols = df.columns[df.dtypes.eq('object')]
    return df[cols].apply(pd.to_numeric, errors='coerce')
