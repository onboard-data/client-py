import requests
import urllib.parse


def divide_chunks(l, n):
    # looping till length l
    for i in range(0, len(l), n):
        yield l[i:i + n]


class APIClient:

    def __init__(self, api_url, user=None, pw=None, api_key=None):
        self._api_url = api_url
        self._user = user
        self._pw = pw
        self._api_key = api_key
        self._token = None
        if not (api_key or (user and pw)):
            raise TypeError("Need one of: user & pw or an api key")

    def _pw_login(self):
        url = '{}/login'.format(self._api_url)
        payload = {
            'login': self._user,
            'password': self._pw,
        }
        headers = {'Content-Type': 'application/json'}
        response = requests.post(url, json=payload, headers=headers)
        self._token = response.json()['userInfo']['token']

    def _api_key_login(self):
        url = '{}/login/api-key'.format(self._api_url)
        payload = {'key': self._api_key}
        response = requests.post(url, json=payload)
        self._token = response.json()['userInfo']['token']

    def _get_token(self):
        if self._token is None:
            if self._api_key:
                self._api_key_login()
            else:
                self._pw_login()
        return self._token

    def auth(self):
        token = self._get_token()
        return {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'}

    def get_all_points(self):
        headers = self.auth()
        buildings_url = '{}/buildings'.format(self._api_url)
        buildings = requests.get(buildings_url, headers=headers).json()
        bldg_ids = list(map(lambda b: b['id'], buildings))
        point_ids = []
        for bldg_id in bldg_ids:
            points_url = '{}/buildings/{}/equipment?points=true' \
                .format(self._api_url, bldg_id)
            equipment = requests.get(points_url, headers=headers).json()
            for e in equipment:
                point_ids += e['points']
        return point_ids

    def get_points_by_ids(self, point_ids):
        point_ids_chunked = list(divide_chunks(point_ids, 500))
        points = []
        for chunk in point_ids_chunked:
            points_str = '[' + ','.join(str(id) for id in chunk) + ']'
            url = '{}/points?point_ids={}'.format(self._api_url, points_str)
            points_chunk = requests.get(url, headers=self.auth()).json()
            points += points_chunk
        return points

    def get_points_by_datasource(self, datasource_hashes):
        datasource_hashes_chunked = list(divide_chunks(datasource_hashes, 125))
        points = []
        for chunk in datasource_hashes_chunked:
            hashes_str = "[" + ','.join([r"'" + c + r"'" for c in chunk]) + "]"
            query = urllib.parse.quote(hashes_str)
            url = '{}/points?datasource_hashes={}'.format(self._api_url, query)
            points_chunk = requests.get(url, headers=self.auth()).json()
            points += points_chunk
        return points

    def get_all_point_types(self):
        url = '{}/pointtypes'.format(self._api_url)
        point_types = requests.get(url, headers=self.auth()).json()
        return point_types

    def get_all_measurements(self):
        url = '{}/measurements'.format(self._api_url)
        measurements = requests.get(url, headers=self.auth()).json()
        return measurements

    def get_all_units(self):
        url = '{}/unit'.format(self._api_url)
        units = requests.get(url, headers=self.auth()).json()
        return units

    def update_point_data(self, updates=[]):
        """Bulk update point data, returns the number of updated points
        updates: an iterable of models.PointDataUpdate objects"""
        url = '{}/points_update'.format(self._api_url)
        json = [u.json() for u in updates]
        patched = requests.post(url, json=json, headers=self.auth()).json()
        return patched

    def send_ingest_stats(self, ingest_stats):
        """Send timing and diagnostic info to the portal
        ingest_stats: an instance of models.IngestStats"""
        url = '{}/ingest-stats'.format(self._api_url)
        json = ingest_stats.json()
        res = requests.post(url, json=json, headers=self.auth())
        if res.status_code > 399:
            raise Exception(f"Exception sending stats: code {res.status_code}")
        return res.json()


class DevelopmentAPIClient(APIClient):
    def __init__(self, user=None, pw=None, api_key=None):
        super().__init__('https://devapi.onboarddata.io', user, pw, api_key)


class ProductionAPIClient(APIClient):
    def __init__(self, user=None, pw=None, api_key=None):
        super().__init__('https://api.onboarddata.io', user, pw, api_key)
