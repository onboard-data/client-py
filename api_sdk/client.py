import urllib.parse
from .util import divide_chunks, json
from .models import PointSelector
from .helpers import ClientBase


class APIClient(ClientBase):
    def __init__(self, api_url, user=None, pw=None, api_key=None, token=None,
                 name=''):
        super().__init__(api_url, user, pw, api_key, token, name)

    @json
    def whoami(self):
        return self.get('/whoami')

    @json
    def get_organizations(self):
        return self.get('/organizations')

    @json
    def get_all_buildings(self):
        return self.get('/buildings')

    @json
    def get_building_equipment(self, building_id):
        return self.get(f'/buildings/{building_id}/equipment?points=true')

    @json
    def select_points(self, selector: PointSelector):
        return self.post('/points/select', json=selector.json())

    def get_all_points(self):
        buildings = self.get_all_buildings()
        bldg_ids = list(map(lambda b: b['id'], buildings))
        point_ids = []
        for bldg_id in bldg_ids:
            equipment = self.get_building_equipment(bldg_id)
            for e in equipment:
                point_ids += e['points']
        return point_ids

    def get_points_by_ids(self, point_ids):
        @json
        def get_points(url):
            return self.get(url)

        point_ids_chunked = list(divide_chunks(point_ids, 500))
        points = []
        for chunk in point_ids_chunked:
            points_str = '[' + ','.join(str(id) for id in chunk) + ']'
            url = f'/points?point_ids={points_str}'
            points_chunk = get_points(url)
            points += points_chunk
        return points

    def get_points_by_datasource(self, datasource_hashes):
        datasource_hashes_chunked = list(divide_chunks(datasource_hashes, 125))
        @json
        def get_points(url):
            return self.get(url)

        points = []
        for chunk in datasource_hashes_chunked:
            hashes_str = "[" + ','.join([r"'" + c + r"'" for c in chunk]) + "]"
            query = urllib.parse.quote(hashes_str)
            url = f'/points?datasource_hashes={query}'
            points_chunk = get_points(url)
            points += points_chunk
        return points

    @json
    def get_all_point_types(self):
        return self.get('/pointtypes')

    @json
    def get_all_measurements(self):
        return self.get('/measurements')

    @json
    def get_all_units(self):
        return self.get('/unit')

    @json
    def query_point_timeseries(self, point_ids, start_time, end_time):
        """Query a timespan for a set of point ids
        point_ids: a list of point ids
        start/end time: ISO formatted timestamp strings e.g. '2019-11-29T20:16:25Z'
        """
        query = {
            'point_ids': point_ids,
            'start_time': start_time,
            'end_time': end_time,
        }
        return self.post('/query', json=query)

    @json
    def update_point_data(self, updates=[]):
        """Bulk update point data, returns the number of updated points
        updates: an iterable of models.PointDataUpdate objects"""
        json = [u.json() for u in updates]
        return self.post('/points_update', json=json)

    @json
    def send_ingest_stats(self, ingest_stats):
        """Send timing and diagnostic info to the portal
        ingest_stats: an instance of models.IngestStats"""
        json = ingest_stats.json()
        return self.post('/ingest-stats', json=json)

    @json
    def copy_point_data(self, point_id_map, start_time, end_time):
        """Copy data between points
        point_id_map: a map of source to destination point id
        start/end: ISO formatted timestamp strings e.g. '2019-11-29T20:16:25Z'
        """
        command = {
            'point_id_map': point_id_map,
            'start_time': start_time,
            'end_time': end_time,
        }
        return self.post('/point-data-copy', json=command)


class DevelopmentAPIClient(APIClient):
    def __init__(self, user=None, pw=None, api_key=None, token=None):
        super().__init__('https://devapi.onboarddata.io', user, pw, api_key, token)


class ProductionAPIClient(APIClient):
    def __init__(self, user=None, pw=None, api_key=None, token=None):
        super().__init__('https://api.onboarddata.io', user, pw, api_key, token)
