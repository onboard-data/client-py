import pandas as pd


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

        point_data = {}
        data_by_point[point_id] = point_data

        for val in point['values']:
            ts = val[ts_index]
            dates.add(ts)
            clean = val[clean_index]
            point_data[ts] = clean

    dates = list(dates)
    dates.sort()
    data = []

    for d in dates:
        row = {'timestamp': d}
        for p in columns[1:]:
            val = data_by_point[p].get(d)
            point_name = point_names.get(p)
            point_col = f"{point_name} - {p}" if point_name else p
            row[point_col] = val
        data.append(row)

    df = pd.DataFrame(data)
    return df
