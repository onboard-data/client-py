import urllib.parse
from datetime import datetime
import deprecation
from orjson import loads
from typing import List, Dict, Any, Optional, Tuple, Union, Iterator
from .util import divide_chunks, json
from .models import PointSelector, PointDataUpdate, IngestStats, \
    TimeseriesQuery, PointData
from .helpers import ClientBase
from .exceptions import OnboardApiException


class APIClient(ClientBase):
    def __init__(self, api_url: str,
                 user: Optional[str] = None, pw: Optional[str] = None,
                 api_key: Optional[str] = None,
                 token: Optional[str] = None,
                 name: str = '') -> None:
        super().__init__(api_url, user, pw, api_key, token, name)

    @json
    def whoami(self) -> Dict[str, str]:
        """returns the current account's information"""
        return self.get('/whoami')

    @json
    def get_account_actions(self) -> List[Dict[str, str]]:
        """returns the action audit log by or affecting the current account"""
        return self.get('/account-actions')

    @json
    def get_users(self) -> List[Dict[str, str]]:
        """returns the list of visible user accounts
          For organization admins this is all users in the organization
          For non-admin users this is just the current account
        """
        return self.get('/users')

    @json
    def get_organizations(self) -> Dict[str, Dict[str, str]]:
        return self.get('/organizations')

    @json
    def get_all_buildings(self) -> List[Dict[str, str]]:
        return self.get('/buildings')

    @json
    def get_tags(self) -> List[Dict[str, str]]:
        """returns a list of all the haystack tags in the system
        For more info, please see https://project-haystack.org/tag"""
        return self.get('/tags')

    @json
    def get_equipment_types(self) -> List[Dict[str, str]]:
        return self.get('/equiptype')

    @json
    def get_building_equipment(self, building_id: int) -> List[Dict[str, Any]]:
        return self.get(f'/buildings/{building_id}/equipment?points=true')

    @json
    def get_equipment_by_ids(self, equipment_ids: List[int]) -> List[Dict[str, object]]:
        body = {'equipment_ids': equipment_ids}
        return self.post('/equipment/query', json=body)

    @json
    def get_building_changelog(self, building_id: int) -> List[Dict[str, object]]:
        """Returns a list of changelog entries for the specified building"""
        return self.get(f'/buildings/{building_id}/changelog')

    @json
    def select_points(self, selector: PointSelector) -> Dict[str, List[int]]:
        """returns point ids based on the provided selector"""
        return self.post('/points/select', json=selector.json())

    def check_data_availability(self,
                                selector: PointSelector
                                ) -> Tuple[Optional[datetime], Optional[datetime]]:
        """Returns a tuple of data timestamps (most stale, most recent) for selected points"""
        @json
        def get_as_json():
            return self.post('/points/data-availability', json=selector.json())

        res = get_as_json()
        oldest = self.ts_to_dt(res['oldest'])
        newest = self.ts_to_dt(res['newest'])
        return (oldest, newest)

    def get_all_points(self) -> List[Dict[str, Any]]:
        """returns all points for all visible buildings"""
        buildings = self.get_all_buildings()
        points: List[Dict[str, Any]] = []
        for b in buildings:
            bldg_id = b['id']
            equipment = self.get_building_equipment(bldg_id)
            for e in equipment:
                points += e['points']
        return points

    def get_all_equipment(self) -> List[Dict]:
        """returns all equipment instances for all visible buildings"""
        buildings = self.get_all_buildings()
        equipment = []
        for b in buildings:
            bldg_id = b['id']
            equipment += self.get_building_equipment(bldg_id)
        return equipment

    def get_points_by_ids(self, point_ids: List[int]) -> List[Dict[str, str]]:
        @json
        def get_points(url):
            return self.get(url)

        points = []
        for chunk in divide_chunks(point_ids, 500):
            points_str = '[' + ','.join(str(id) for id in chunk) + ']'
            url = f'/points?point_ids={points_str}'
            try:
                points_chunk = get_points(url)
            except OnboardApiException as e:
                if '"status": 404' in str(e):
                    continue
                raise e
            points += points_chunk
        return points

    def get_points_by_datasource(self, datasource_hashes: List[str]) \
            -> List[Dict[str, str]]:
        datasource_hashes_chunked = list(divide_chunks(datasource_hashes, 125))

        @json
        def get_points(url):
            return self.get(url)

        points = []
        for chunk in datasource_hashes_chunked:
            hashes_str = "[" + ','.join([r"'" + c + r"'" for c in chunk]) + "]"
            query = urllib.parse.quote(hashes_str)
            url = f'/points?datasource_hashes={query}'
            try:
                points_chunk = get_points(url)
            except OnboardApiException as e:
                if '"status": 404' in str(e):
                    continue
                raise e
            points += points_chunk
        return points

    @json
    def get_all_point_types(self) -> List[Dict[str, str]]:
        return self.get('/pointtypes')

    @json
    def get_all_measurements(self) -> List[Dict[str, str]]:
        return self.get('/measurements')

    @json
    def get_all_units(self) -> List[Dict[str, str]]:
        return self.get('/unit')

    @deprecation.deprecated(deprecated_in="1.3.0",
                            details="Use stream_point_timeseries instead")
    @json
    def query_point_timeseries(self, point_ids: List[int],
                               start_time: Union[str, datetime],
                               end_time: Union[str, datetime]) -> List[Dict[str, Any]]:
        """Query a timespan for a set of point ids
        point_ids: a list of point ids
        start/end time: ISO formatted timestamp strings e.g. '2019-11-29T20:16:25Z' or a datetime
        """
        query = {
            'point_ids': point_ids,
            'start_time': self.dt_to_str(start_time),
            'end_time': self.dt_to_str(end_time),
        }
        return self.post('/query', json=query)

    def stream_point_timeseries(self, query: TimeseriesQuery) -> Iterator[PointData]:
        """Query a time interval for an explicit set of point ids or
        with a selector which describes which sensors to include.

        Example values docmentaed on the model tab here:
            https://api.onboarddata.io/doc/#/buildings%3Aread/post_query_v2
        """

        @json
        def query_call():
            return self.post('/query-v2', json=query.json(), stream=True,
                             headers={'Accept': 'application/x-ndjson'})
        query_call.raw_response = True  # type: ignore[attr-defined]

        point_data = PointData.__pydantic_model__.construct  # type: ignore[attr-defined]

        with query_call() as res:
            for line in res.iter_lines(chunk_size=20 * 1024):
                parsed = loads(line)
                yield point_data(**parsed)

    @json
    def update_point_data(self, updates: List[PointDataUpdate] = []) -> None:
        """Bulk update point data, returns the number of updated points
        updates: an iterable of models.PointDataUpdate objects"""
        for batch in divide_chunks(updates, 500):
            json = [u.json() for u in batch]
            self.post('/points_update', json=json).raise_for_status()

    @json
    def send_ingest_stats(self, ingest_stats: IngestStats) -> None:
        """Send timing and diagnostic info to the portal
        ingest_stats: an instance of models.IngestStats"""
        json = ingest_stats.json()
        self.post('/ingest-stats', json=json).raise_for_status()

    @json
    def get_ingest_stats(self) -> List[Dict[str, str]]:
        """returns ingest stats for all buildings"""
        return self.get('/ingest-stats')

    @json
    def get_alerts(self) -> List[Dict[str, str]]:
        """returns a list of active alerts for all buildings"""
        return self.get('/alerts')

    @json
    def copy_point_data(self, point_id_map: Dict[int, int],
                        start_time: Union[str, datetime],
                        end_time: Union[str, datetime]) -> str:
        """Copy data between points
        point_id_map: a map of source to destination point id
        start/end: ISO formatted timestamp strings e.g. '2019-11-29T20:16:25Z'
        returns: a string describing the operation
        """
        command = {
            'point_id_map': point_id_map,
            'start_time': self.dt_to_str(start_time),
            'end_time': self.dt_to_str(end_time),
        }
        return self.post('/point-data-copy', json=command)


class DevelopmentAPIClient(APIClient):
    def __init__(self, user=None, pw=None, api_key=None, token=None) -> None:
        super().__init__('https://devapi.onboarddata.io',
                         user, pw, api_key, token)


class ProductionAPIClient(APIClient):
    def __init__(self, user: Optional[str] = None, pw: Optional[str] = None,
                 api_key: Optional[str] = None,
                 token: Optional[str] = None) -> None:
        super().__init__('https://api.onboarddata.io',
                         user, pw, api_key, token)
