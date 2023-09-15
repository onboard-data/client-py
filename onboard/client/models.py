import math
from datetime import datetime, timezone
from typing import List, Optional, Union, Dict
from dataclasses import field
from pydantic.dataclasses import dataclass
from pydantic import validator, BaseModel


class PointDataUpdate(object):
    """Model for bulk-updating a point's data value and timestamp"""
    __slots__ = ['point_id', 'value', 'last_updated', 'first_updated']

    def __init__(self, point_id: int, value: Union[str, float, int],
                 last_updated: datetime, first_updated: Optional[datetime] = None) -> None:
        errors: List[str] = []
        if not isinstance(point_id, int):
            errors.append(f"point id must be an integer, saw {point_id}")
        self.point_id = point_id
        self.value = value
        if not isinstance(last_updated, datetime):
            errors.append(f"last updated must be a datetime, saw {last_updated}")
        self.last_updated = last_updated
        if first_updated is not None and not isinstance(first_updated, datetime):
            errors.append(f"first updated must be a datetime, saw {first_updated}")
        self.first_updated = first_updated
        if errors:
            raise ValueError(f"Invalid PointDataUpdate: {', '.join(errors)}")

    def json(self):
        utc_ts_s = self.last_updated.replace(tzinfo=timezone.utc).timestamp()
        first_ts = None
        if self.first_updated is not None:
            first_ts = 1000 * self.first_updated.replace(tzinfo=timezone.utc).timestamp()
        return {'id': self.point_id, 'value': self.value,
                'last_updated': utc_ts_s * 1000, 'first_updated': first_ts}


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
    # id, name, short_name or name_abbr
    orgs: List[Union[int, str]] = field(default_factory=list)
    # id or name
    buildings: List[Union[int, str]] = field(default_factory=list)

    # returned points are the superset of these three selectors
    point_ids: List[int] = field(default_factory=list)
    point_names: List[str] = field(default_factory=list)
    point_hashes: List[str] = field(default_factory=list)
    point_topics: List[str] = field(default_factory=list)

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

    Unit conversion preferences are expressed as a map from measurement name to unit name, e.g.
    {'temperature': 'f', 'power': 'kw'}

    See https://portal.onboarddata.io/account?tab=unitPrefs for available measurements and units
    """
    start: datetime  # timezone required
    end: datetime  # timezone required
    selector: Optional[PointSelector] = None
    point_ids: List[int] = field(default_factory=list)
    units: Dict[str, str] = field(default_factory=dict)  # unit conversion preferences

    @validator('point_ids')
    def points_or_selector_required(cls, point_ids, values):
        has_points = len(point_ids) > 0
        has_selector = values.get('selector') is not None
        if has_points == has_selector:
            raise ValueError("Exactly one of 'point_ids' or 'selector' is required")
        return point_ids

    @validator('start', 'end')
    def times_valid(cls, value, values):
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
class PointData(BaseModel):
    point_id: int
    raw: str
    unit: str
    columns: List[str]
    values: List[List[Union[str, float, int, None]]]
