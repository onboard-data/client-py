# Onboard Portal Python SDK

This package provides Python bindings to Onboard Data's [building data API](https://portal.onboarddata.io). For more details, you can consult the API's [swagger documentation](https://api.onboarddata.io/doc/).

## API Access

You'll need an API key or existing account in order to use this client. If you don't have one and would like to start prototyping against an example building please [request a key here](https://www.onboarddata.io/apirequest).

## Client usage example

First, you'll need to install the client (requires Python >= 3.6 )

```bash
$ pip install onboard.client
```

Now you can use the client to fetch timeseries data for sensors by building or based on type.

```python
from onboard.client import OnboardClient
client = OnboardClient(api_key='your-key-here')

client.whoami()  # verify access & connectivity

client.get_all_point_types()  # retrieve available types of sensors

# retrieve the past 6 hours of data for sensors measuring CO2 ppm
import datetime
from onboard.client.models import PointSelector

query = PointSelector()
query.point_types = ['Zone Carbon Dioxide']
query.buildings = ['Example Building']
selection = client.select_points(query)
end = datetime.datetime.utcnow()
start = end - datetime.timedelta(hours=6)

sensor_metadata = client.get_points_by_ids(selection['points'])
sensor_data = client.query_point_timeseries(selection['points'], start, end)
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
