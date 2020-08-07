import math
from datetime import datetime, timezone


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


class PointSelector:
    """A flexible interface to allow users to select sets of points"""
    def __init__(self) -> None:
        self.orgs = []  # id, name or short_name
        self.buildings = []  # id or name
        # returned points are the superset of these three selectors
        self.point_ids = []  # ints
        self.point_names = []  # strings
        self.point_hashes = []  # strings
        self.point_types = []  # PointType.id or PointType.tag_name
        self.equipment = []  # Equipment.id or Equipment.suffix
        self.equipment_types = []  # EquipmentType.id or EquipmentType.tag_name
        self.updated_since = None  # datetime

    def json(self):
        ts = self.updated_since.timestamp() * 1000.0 if self.updated_since is not None else None
        dict = {k: getattr(self, k) for k in vars(self)}
        return {**dict, 'updated_since': ts}

    def __eq__(self, other):
        if not isinstance(other, PointSelector):
            return False
        return self.__dict__ == other.__dict__

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
