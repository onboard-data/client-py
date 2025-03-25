# Onboard Portal Python SDK

![PyPI](https://img.shields.io/pypi/v/onboard.client)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/onboard.client)
![PyPI - Status](https://img.shields.io/pypi/status/onboard.client)
![PyPI - License](https://img.shields.io/pypi/l/onboard.client)

This package provides Python bindings to Onboard Data's [building data API](https://portal.onboarddata.io).
For more details, you can navigate to the API & Docs Page to read the Getting Started Documentation section in the portal.
You'll have access to this page once you've signed up for our sandbox or you've been given access to your organization's account.

## API Access

You'll need an API key or existing account in order to use this client. If you don't have one and would like to start prototyping against an example building please [request a key here](https://onboarddata.io/sandbox).

Once you have a key, data access is explicitly granted by attaching one or more 'scopes' to the key. Our endpoints are grouped by scope on the [swagger documentation](https://api.onboarddata.io/swagger/) viewer.

You can also learn more about this client [on our docs!](https://onboard-api-wrappers-documentation.readthedocs.io/en/latest/index.html)

## Client usage example

First, you'll need to install the client (requires Python >= `3.8`)

```bash
$ pip install onboard.client
```

Now you can use the client to fetch timeseries data for sensors by building or based on type. This example requires an API key with the scopes `general` and `buildings:read`.

```python
from onboard.client import OnboardClient
client = OnboardClient(api_key='ob-p-your-key-here')

client.whoami()  # verify access & connectivity

client.get_all_point_types()  # retrieve available types of sensors

# retrieve the past 6 hours of data for sensors measuring CO2 ppm
from datetime import datetime, timezone, timedelta
from onboard.client.models import PointSelector, TimeseriesQuery, PointData
from typing import List

query = PointSelector()
query.point_types = ['Zone Carbon Dioxide']
query.buildings = ['Office Building']  # one of the example buildings available in the sandbox
selection = client.select_points(query)
end = datetime.utcnow().replace(tzinfo=timezone.utc)
start = end - timedelta(hours=6)

timeseries_query = TimeseriesQuery(point_ids=selection['points'], start=start, end=end)  # Or `TimeseriesQuery(selector=query, ...)`

sensor_metadata = client.get_points_by_ids(selection['points'])
sensor_data: List[PointData] = list(client.stream_point_timeseries(timeseries_query))
```

### Retries
The OnboardClient also exposes urllib3.util.retry.Retry to allow configuring retries in the event of a network issue. An example for use would be

```python
from onboard.client import OnboardClient
from urlilib3.util.retry import Retry

retry = Retry(total=3, backoff_factor=0.3, status_forcelist=(500, 502, 504))
client = OnboardClient(api_key='ob-p-your-key-here', retry=retry)

```

## Staging client usage

We provide an additional client object for users who wish to modify their building equipment and points in the "staging area" before those metadata are promoted to the primary tables. API keys used with the staging client require the `staging` scope, and your account must be authorized to perform `READ` and `UPDATE` operations on the building itself.

The staging area provides a scratchpad interface, where arbitrary additional columns can be added to points or equipment by using the prefix `p.` or `e.`. Any un-prefixed, user-added columns will be attached to points. Each update dictionary can modify a point, equipment or both at the same time (which implicitly reparents the point to the equipment). Each update should `p.topic` and/or `e.equip_id` to identify to the system where to apply the write. If a `topic` and `equip_id` are provided together in the same object then the system will associate that point with that equipment.

Updates use `PATCH` semantics, so only provided fields will be written to. Check-and-set concurrency control is available. To use it, include a `.cas` field with a current value to verify before processing the update. Please see the `update` object in the example below for more details.

The staging client supports the same urllib3.util.retry.Retry support that the standard client has.

```python
from onboard.client.staging import OnboardStagingClient

staging = OnboardStagingClient(api_key='ob-p-your-key-here')

buildings = client.get_all_buildings()  # using OnboardClient from above example
all_building_details = staging.get_staging_building_details()  # a list of building-level staging information objects

building_id: int = 0  # yours here

points = staging.get_staging_points(building_id)
equipment = staging.get_staging_equipment(building_id)

point_update = [
    # keys to identify the point we are modifying
    {
        'topic':'org/building/4242/my-sensor',
        # an update of related equipment: equip_names
        'equip_names': ["equip_name1", "equip_name2"],
        # an optional check-and-set guard for the equip relation update
        'modified.cas': '2025-03-13 14:44:24.133067+00:00'
    }
]
equip_update = [
    # keys to identify the equipment we are modifying
    {
        'name':'ahu-1',
        # an update to rename equipment
        'new_name': 'ahu-2',
    }
]
modified_point = staging.update_staging_points(building_id, point_update)
modified_equipment = staging.update_staging_equipment(building_id, equipment_update)
```

## License

 Copyright 2018-2024 Onboard Data Inc

 Licensed under the Apache License, Version 2.0 (the "License");
 you may not use this file except in compliance with the License.
 You may obtain a copy of the License at

     http://www.apache.org/licenses/LICENSE-2.0

 Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an "AS IS" BASIS,
 WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 See the License for the specific language governing permissions and
 limitations under the License.
