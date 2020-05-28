import requests
import datetime
from requests.models import Response
from typing import Optional, Union
from .exceptions import OnboardApiException
from .util import json

USER_AGENT = 'Onboard Py-SDK'


class ClientBase:
    """Base class that implements HTTP methods against the API on top of requests"""
    def __init__(self, api_url: Optional[str],
                 user: Optional[str], pw: Optional[str],
                 api_key: Optional[str],
                 token: Optional[str],
                 name: [Optional[str]]) -> None:
        self.api_url = api_url
        self.api_key = api_key
        self.user = user
        self.pw = pw
        self.token = token
        self.name = name
        if not (api_key or token or (user and pw)):
            raise OnboardApiException("Need one of: user & pw, token or api_key")
        self.session = None

    def __session(self):
        if self.session is None:
            self.session = requests.Session()
            self.session.headers.update(self.headers())
            self.session.headers.update(self.auth())
        return self.session

    def headers(self):
        agent = f"{USER_AGENT} ({self.name})" if self.name else USER_AGENT
        return {'Content-Type': 'application/json',
                'User-Agent': agent}

    def auth(self):
        token = self.__get_token()
        return {'Authorization': f'Bearer {token}'}

    @json
    def __pw_login(self):
        payload = {
            'login': self.user,
            'password': self.pw,
        }
        return self.post('/login', json=payload)

    @json
    def __api_key_login(self):
        payload = {'key': self.api_key}
        return self.post('/login/api-key', json=payload)

    def __get_token(self):
        if self.token is None:
            if self.api_key:
                login_res = self.__api_key_login()
            else:
                login_res = self.__pw_login()
            self.token = login_res['access_token']

        if self.token is None:
            raise OnboardApiException("Not authorized")

        return self.token

    def __repr__(self) -> str:
        return f"OnboardSdk(url={self.api_url})"

    def url(self, url: str) -> str:
        if not url.startswith('http'):
            return self.api_url + url
        return url

    def get(self, url: str, **kwargs) -> Response:
        return self.__session().get(self.url(url), **kwargs)

    def delete(self, url: str, **kwargs) -> Response:
        return self.__session().delete(self.url(url), **kwargs)

    def put(self, url: str, **kwargs) -> Response:
        return self.__session().put(self.url(url), **kwargs)

    def post(self, url: str, **kwargs) -> Response:
        return self.__session().post(self.url(url), **kwargs)

    def ts_to_dt(self, ts: Optional[float]) -> datetime.datetime:
        if ts is None:
            return None
        return datetime.datetime.utcfromtimestamp(ts / 1000.0)

    def dt_to_str(self, dt: Union[str, datetime.datetime]) -> str:
        if isinstance(dt, str):
            return dt
        if dt.tzinfo is None:
            return dt.isoformat() + "Z"
        return dt.isoformat()
