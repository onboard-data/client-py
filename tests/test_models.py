# type: ignore

from datetime import datetime, timezone
from onboard.client.models import TimeseriesQuery, PointData


def test_timeseries_query():
    dict = {
        'point_ids': [1],
        'start': datetime.utcnow().replace(tzinfo=timezone.utc),
        'end': datetime.utcnow().replace(tzinfo=timezone.utc),
    }
    TimeseriesQuery(**dict)


def test_point_data():
    dict = {
        'point_id': 1,
        'raw': 'F',
        'unit': 'C',
        'columns': ['timestamp', 'raw', 'C'],
        'values': [
            ['2020-12-16', 32.0, 0.0],
        ]
    }
    PointData(**dict)


def test_point_data_none_value():
    dict = {
        'point_id': 1,
        'raw': 'F',
        'unit': 'C',
        'columns': ['timestamp', 'raw', 'C'],
        'values': [
            ['2020-12-16', None, 0.0],
        ]
    }
    PointData(**dict)
