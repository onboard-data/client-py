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
