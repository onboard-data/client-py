import requests
import urllib.parse


class APIClient:

    def __init__(self, api_url, user, pw):
        self._api_url = api_url
        self._user = user
        self._pw = pw
        self._token = None

    def _get_token(self):
        if self._token is None:
            url = '{}/login'.format(self._api_url)
            payload = {
                'login': self._user,
                'password': self._pw,
            }
            headers = { 'Content-Type': 'application/json'}
            response = requests.post(url, json=payload, headers=headers)
            self._token = response.json()['userInfo']['token']
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
            points_url = '{}/buildings/{}/equipment?points=true'.format(self._api_url, bldg_id)
            equipment = requests.get(points_url, headers=headers).json()
            for e in equipment:
                point_ids += e['points']
        return point_ids

    def divide_chunks(self, l, n):
        # looping till length l
        for i in range(0, len(l), n):
            yield l[i:i + n]

    def get_points_by_ids(self, point_ids):
        point_ids_chunked = list(self.divide_chunks(point_ids, 500))
        points = []
        for chunk in point_ids_chunked:
            points_str = '[' + ','.join(str(id) for id in chunk) + ']'
            url = '{}/points?point_ids={}'.format(self._api_url, points_str)
            points_chunk = requests.get(url, headers=self.auth()).json()
            points += points_chunk
        return points

    def get_points_by_datasource(self, datasource_hashes):
        datasource_hashes_chunked = list(self.divide_chunks(datasource_hashes, 125))
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
