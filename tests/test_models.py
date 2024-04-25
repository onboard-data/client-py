from datetime import datetime, timezone

from onboard.client.models import TimeseriesQuery, PointData


def test_timeseries_query():
    return TimeseriesQuery(
        point_ids=[1],
        start=datetime.utcnow().replace(tzinfo=timezone.utc),
        end=datetime.utcnow().replace(tzinfo=timezone.utc),
    )


def test_point_data():
    PointData(
        point_id=1,
        raw='F',
        unit='C',
        columns=['timestamp', 'raw', 'C'],
        values=[
            ['2020-12-16', 32.0, 0.0],
        ]
    )


def test_point_data_none_value():
    PointData(
        point_id=1,
        raw='F',
        unit='C',
        columns=['timestamp', 'raw', 'C'],
        values=[
            ['2020-12-16', None, 0.0],
        ]
    )


def test_point_data_extra_keys():
    constructed = PointData(
        point_id=1,
        raw='F',
        unit='C',
        columns=['timestamp', 'raw', 'C'],
        values=[
            ['2020-12-16', 32.0, 0.0],
        ],
        foo='bar',
        zip={'zap': 1},
    )
    assert constructed.foo == 'bar'  # type: ignore[attr-defined]
    assert constructed.point_id == 1
