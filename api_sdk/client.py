import requests
import json


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
            response = requests.post(url, data=json.dumps(payload), headers=headers)
            self._token = response.json()['userInfo']['token']
        return self._token

    def get_all_point_ids(self):
        token = self._get_token()
        buildings_url = '{}/buildings'.format(self._api_url)
        headers = {'Authorization': 'Bearer {}'.format(token)}
        buildings = requests.get(buildings_url, headers=headers).json()
        bldg_ids = list(map(lambda b: b['id'], buildings))
        point_ids = []
        for bldg_id in bldg_ids:
            points_url = '{}/buildings/{}/equipment?points=true'.format(self._api_url, bldg_id)
            equipment = requests.get(points_url, headers=headers).json()
            for e in equipment:
                point_ids += map(lambda p: p['id'], e['points'])
        return point_ids

    def get_points_by_ids(self, point_ids):
        token = self._get_token()
        points_str = '[' + ','.join(str(id) for id in point_ids) + ']'
        url = '{}/points?point_ids={}'.format(self._api_url, points_str)
        headers = {'Authorization': 'Bearer {}'.format(token)}
        points = requests.get(url, headers=headers).json()
        return points

    def get_all_point_types(self):
        token = self._get_token()
        url = '{}/pointtypes'.format(self._api_url)
        headers = {'Authorization': 'Bearer {}'.format(token)}
        point_types = requests.get(url, headers=headers).json()
        return point_types

    def get_all_measurements(self):
        token = self._get_token()
        url = '{}/measurements'.format(self._api_url)
        headers = {'Authorization': 'Bearer {}'.format(token)}
        measurements = requests.get(url, headers=headers).json()
        return measurements

    def get_all_units(self):
        token = self._get_token()
        url = '{}/unit'.format(self._api_url)
        headers = {'Authorization': 'Bearer {}'.format(token)}
        units = requests.get(url, headers=headers).json()
        return units
