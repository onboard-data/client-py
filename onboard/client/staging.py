from typing import List, Dict, Any
from .helpers import ClientBase
from .util import json


class StagingClient(ClientBase):
    def __init__(self, api_url: str,
                 api_key: str, name: str = '') -> None:
        super().__init__(api_url, api_key=api_key, name=name,
                         user=None, pw=None, token=None)

    @json
    def get_staging_building_details(self) -> List[Dict]:
        return self.get('/staging')

    @json
    def update_building_details(self, building_id: int,
                                details: Dict[str, Any]) -> Dict:
        return self.patch(f"/staging/{building_id}/details", json=details)

    @json
    def get_staged_equipment(self, building_id: int) -> Dict:
        return self.get(f'/staging/{building_id}')

    def get_staged_equipment_csv(self, building_id: int) -> str:
        @json
        def get_csv():
            return self.get(f'/staging/{building_id}',
                            headers={'Accept': 'text/csv'})

        get_csv.raw_response = True  # type: ignore[attr-defined]
        return get_csv().text

    @json
    def update_staged_equipment(self, building_id: int, updates: List[Dict]) -> Dict:
        return self.post(f'/staging/{building_id}', json=updates)


class OnboardStagingClient(StagingClient):
    def __init__(self, api_key: str) -> None:
        super().__init__('https://api.onboarddata.io', api_key)
