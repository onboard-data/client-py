# type: ignore

from datetime import datetime, timezone
from typing import Dict, Any

from onboard.client.models import TimeseriesQuery, PointData


def test_timeseries_query():
    dict = {
        'point_ids': [1],
        'start': datetime.utcnow().replace(tzinfo=timezone.utc),
        'end': datetime.utcnow().replace(tzinfo=timezone.utc),
    }
    TimeseriesQuery(**dict)


def construct(dict: Dict[str, Any]) -> PointData:
    try:
        # Pydantic v1
        return PointData.__pydantic_model__.construct(**dict)  # type: ignore[attr-defined]
    except AttributeError:
        # Pydantic v2
        return PointData.model_construct(**dict)  # type: ignore[attr-defined]


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
    construct(dict)


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
    construct(dict)


def test_point_data_extra_keys():
    dict = {
        'point_id': 1,
        'raw': 'F',
        'unit': 'C',
        'columns': ['timestamp', 'raw', 'C'],
        'values': [
            ['2020-12-16', 32.0, 0.0],
        ],
        'foo': 'bar',
        'zip': {'zap': 1},
    }
    constructed = construct(dict)
    assert constructed.foo == 'bar'
    assert constructed.point_id == 1
