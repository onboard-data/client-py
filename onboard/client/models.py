import math
from datetime import datetime, timezone
from typing import List, Optional, Union
from dataclasses import field
from pydantic.dataclasses import dataclass
from pydantic import validator


class PointDataUpdate(object):
    """Model for bulk-updating a point's data value and timestamp"""
    __slots__ = ['point_id', 'value', 'last_updated']

    def __init__(self, point_id, value, last_updated):
        errors = []
        if not isinstance(point_id, int):
            errors.append(f"point id must be an integer, saw {point_id}")
        self.point_id = point_id
        self.value = value
        if not isinstance(last_updated, datetime):
            errors.append(f"last updated must be a datetime, saw {last_updated}")
        self.last_updated = last_updated
        if errors:
            raise ValueError(f"Invalid PointDataUpdate: {', '.join(errors)}")

    def json(self):
        utc_ts_s = self.last_updated.replace(tzinfo=timezone.utc).timestamp()
        return {'id': self.point_id,
                'value': self.value,
                'last_updated': utc_ts_s * 1000}


class IngestStats(object):
    def __init__(self):
        self._points = []
        self._building = {}

    def summary(self, info):
        # infos, errors, num_points, sample_points, etc
        for k, v in info.items():
            if k == 'elapsed':
                self.elapsed(v)
            else:
                self._building[k] = v

    def add_points(self, points):
        self._points += points

    def elapsed(self, elapsed):
        self._building['processing_time_ms'] = math.floor(elapsed.total_seconds() * 1000)

    def json(self):
        return {
            'building': self._building,
            'points': self._points,
        }


@dataclass
class PointSelector:
    """A flexible interface to allow users to select sets of points"""
    # id, name or short_name
    orgs: List[Union[int, str]] = field(default_factory=list)
    # id or name
    buildings: List[Union[int, str]] = field(default_factory=list)

    # returned points are the superset of these three selectors
    point_ids: List[int] = field(default_factory=list)
    point_names: List[str] = field(default_factory=list)
    point_hashes: List[str] = field(default_factory=list)

    # allow filtering out points w/o recent data
    updated_since: Optional[datetime] = None

    # PointType.id or PointType.tag_name
    point_types: List[Union[int, str]] = field(default_factory=list)

    # Equipment.id or Equipment.suffix
    equipment: List[Union[int, str]] = field(default_factory=list)
    # EquipmentType.id or EquipmentType.tag_name
    equipment_types: List[Union[int, str]] = field(default_factory=list)

    def json(self):
        ts = self.updated_since.timestamp() * 1000.0 if self.updated_since is not None else None
        dict = {k: getattr(self, k) for k in vars(self)
                if not k.startswith('__')}
        return {**dict, 'updated_since': ts}

    @staticmethod
    def from_json(dict):
        ps = PointSelector()
        for k in ps.__dict__.keys():
            val = dict.get(k, [])
            if k == 'updated_since':
                val = dict.get(k)
                if val is not None:
                    val = datetime.fromtimestamp(val / 1000.0)
            setattr(ps, k, val)
        return ps


@dataclass
class TimeseriesQuery:
    """Parameters needed to fetch timeseries data.

    Exactly one of point_ids or selector is required

    Note: the server may perform additional validation and reject queries
    which are constructable by the client

    For example values please refer to
        https://api.onboarddata.io/doc/#/buildings%3Aread/post_query_v2
    """
    start: datetime  # timezone required, year must be >= 2019
    end: datetime  # timezone required, year must be >= 2019
    selector: Optional[PointSelector] = None
    point_ids: List[int] = field(default_factory=list)

    units: List[str] = field(default_factory=list)

    @validator('point_ids')
    def points_or_selector_required(cls, point_ids, values):
        has_points = len(point_ids) > 0
        has_selector = values.get('selector') is not None
        if has_points == has_selector:
            raise ValueError("Exactly one of 'point_ids' or 'selector' is required")
        return point_ids

    @validator('start', 'end')
    def times_valid(cls, value, values):
        if value.year < 2019:
            raise ValueError(f'Time boundaries must be in 2019 or later, saw: {value}')
        if value.tzinfo is None:
            raise ValueError(f'Time boundaries require a timezone, saw: {value}')
        return value

    def json(self):
        return {
            'start': self.start.timestamp(),
            'end': self.end.timestamp(),
            'selector': self.selector.json() if self.selector is not None else None,
            'point_ids': self.point_ids,
            'units': self.units,
        }


@dataclass
class PointData:
    point_id: int
    raw: str
    unit: str
    columns: List[str]
    values: List[List[Union[str, float, int, None]]]
