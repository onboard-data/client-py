import requests
import urllib.parse
from .util import divide_chunks, json
from .exceptions import OnboardApiException
from .models import PointSelector
from typing import Any


HEADERS = {
    'Content-Type': 'application/json',
    'User-Agent': 'Onboard Py-SDK',
}


class APIClient:

    def __init__(self, api_url, user=None, pw=None, api_key=None, token=None):
        self._api_url = api_url
        self._user = user
        self._pw = pw
        self._api_key = api_key
        self._token = token
        if not (api_key or token or (user and pw)):
            raise OnboardApiException("Need one of: user & pw, token or an api key")

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, APIClient):
            return self.__dict__ == other.__dict__
        return False

    @json
    def __pw_login(self):
        url = '{}/login'.format(self._api_url)
        payload = {
            'login': self._user,
            'password': self._pw,
        }
        return requests.post(url, json=payload, headers=HEADERS)

    @json
    def __api_key_login(self):
        url = '{}/login/api-key'.format(self._api_url)
        payload = {'key': self._api_key}
        return requests.post(url, json=payload, headers=HEADERS)

    def _get_token(self):
        if self._token is None:
            if self._api_key:
                login_res = self.__api_key_login()
            else:
                login_res = self.__pw_login()
            self._token = login_res['userInfo']['token']

        if self._token is None:
            raise OnboardApiException("Not authorized")

        return self._token

    def auth(self):
        token = self._get_token()
        return {'Authorization': f'Bearer {token}', **HEADERS}

    @json
    def whoami(self):
        url = f"{self._api_url}/whoami"
        return requests.get(url, headers=self.auth())

    @json
    def get_all_buildings(self):
        url = f"{self._api_url}/buildings"
        return requests.get(url, headers=self.auth())

    @json
    def get_building_equipment(self, building_id):
        points_url = '{}/buildings/{}/equipment?points=true' \
            .format(self._api_url, building_id)
        return requests.get(points_url, headers=self.auth())

    @json
    def select_points(self, selector: PointSelector):
        url = f"{self._api_url}/points/select"
        return requests.post(url, headers=self.auth(), json=selector.json())

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
            return requests.get(url, headers=self.auth())

        point_ids_chunked = list(divide_chunks(point_ids, 500))
        points = []
        for chunk in point_ids_chunked:
            points_str = '[' + ','.join(str(id) for id in chunk) + ']'
            url = '{}/points?point_ids={}'.format(self._api_url, points_str)
            points_chunk = get_points(url)
            points += points_chunk
        return points

    def get_points_by_datasource(self, datasource_hashes):
        datasource_hashes_chunked = list(divide_chunks(datasource_hashes, 125))
        @json
        def get_points(url):
            return requests.get(url, headers=self.auth())

        points = []
        for chunk in datasource_hashes_chunked:
            hashes_str = "[" + ','.join([r"'" + c + r"'" for c in chunk]) + "]"
            query = urllib.parse.quote(hashes_str)
            url = '{}/points?datasource_hashes={}'.format(self._api_url, query)
            points_chunk = get_points(url)
            points += points_chunk
        return points

    @json
    def get_all_point_types(self):
        url = '{}/pointtypes'.format(self._api_url)
        return requests.get(url, headers=self.auth())

    @json
    def get_all_measurements(self):
        url = '{}/measurements'.format(self._api_url)
        return requests.get(url, headers=self.auth())

    @json
    def get_all_units(self):
        url = '{}/unit'.format(self._api_url)
        return requests.get(url, headers=self.auth())

    @json
    def query_point_timeseries(self, point_ids, start_time, end_time):
        """Query a timespan for a set of point ids
        point_ids: a list of point ids
        start/end time: ISO formatted timestamp strings e.g. '2019-11-29T20:16:25Z'
        """
        url = '{}/query'.format(self._api_url)
        query = {
            'point_ids': point_ids,
            'start_time': start_time,
            'end_time': end_time,
        }
        return requests.post(url, json=query, headers=self.auth())

    @json
    def update_point_data(self, updates=[]):
        """Bulk update point data, returns the number of updated points
        updates: an iterable of models.PointDataUpdate objects"""
        url = '{}/points_update'.format(self._api_url)
        json = [u.json() for u in updates]
        return requests.post(url, json=json, headers=self.auth())

    @json
    def send_ingest_stats(self, ingest_stats):
        """Send timing and diagnostic info to the portal
        ingest_stats: an instance of models.IngestStats"""
        url = '{}/ingest-stats'.format(self._api_url)
        json = ingest_stats.json()
        return requests.post(url, json=json, headers=self.auth())


class DevelopmentAPIClient(APIClient):
    def __init__(self, user=None, pw=None, api_key=None, token=None):
        super().__init__('https://devapi.onboarddata.io', user, pw, api_key, token)


class ProductionAPIClient(APIClient):
    def __init__(self, user=None, pw=None, api_key=None, token=None):
        super().__init__('https://api.onboarddata.io', user, pw, api_key, token)
