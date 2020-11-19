# Onboard Portal Python SDK

![PyPI](https://img.shields.io/pypi/v/onboard.client)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/onboard.client)
![PyPI - Status](https://img.shields.io/pypi/status/onboard.client)
![PyPI - License](https://img.shields.io/pypi/l/onboard.client)

This package provides Python bindings to Onboard Data's [building data API](https://portal.onboarddata.io). For more details, you can consult the API's [swagger documentation](https://api.onboarddata.io/doc/).

## API Access

You'll need an API key or existing account in order to use this client. If you don't have one and would like to start prototyping against an example building please [request a key here](https://www.onboarddata.io/apirequest).

Once you have a key, data access is explicitly granted by attaching one or more 'scopes' to the key. Our endpoints are grouped by scope on the [swagger documentation](https://api.onboarddata.io/doc/) viewer.

## Client usage example

First, you'll need to install the client (requires Python >= 3.7 )

```bash
$ pip install onboard.client
```

Now you can use the client to fetch timeseries data for sensors by building or based on type. This example requires a key with the scopes `auth`, `general` and `buildings:read`.

```python
from onboard.client import OnboardClient
client = OnboardClient(api_key='your-key-here')

client.whoami()  # verify access & connectivity

client.get_all_point_types()  # retrieve available types of sensors

# retrieve the past 6 hours of data for sensors measuring CO2 ppm
from datetime import datetime, timezone, timedelta
from onboard.client.models import PointSelector, TimeseriesQuery, PointData
from typing import List

query = PointSelector()
query.point_types = ['Zone Carbon Dioxide']
query.buildings = ['Example Building']
selection = client.select_points(query)
end = datetime.utcnow().replace(tzinfo=timezone.utc)
start = end - timedelta(hours=6)

timeseries_query = TimeseriesQuery(point_ids=selection['points'], start=start, end=end)  # Or `TimeseriesQuery(selector=query, ...)`

sensor_metadata = client.get_points_by_ids(selection['points'])
sensor_data: List[PointData] = list(client.stream_point_timeseries(timeseries_query))
```

## License

 Copyright 2018-2020 Onboard Data Inc

 Licensed under the Apache License, Version 2.0 (the "License");
 you may not use this file except in compliance with the License.
 You may obtain a copy of the License at

     http://www.apache.org/licenses/LICENSE-2.0

 Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an "AS IS" BASIS,
 WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 See the License for the specific language governing permissions and
 limitations under the License.
