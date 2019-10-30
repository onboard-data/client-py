import os
import sys
from api_sdk.client import ProductionAPIClient
from api_sdk.util import points_df_from_timeseries


def usage():
    print("Usage:")
    print("python time-series.py <building name or id> <equipment type name + suffix> <start date> <end date>")
    print("e.g. python time-series.py \"Science Park\" \"AHU SSAC-1\" 2019-10-15 2019-10-31")
    sys.exit(1)


def get_building_id(client, building):
    try:
        return int(building)
    except ValueError:
        pass  # must have gotten a building name instead
    buildings = client.get_all_buildings()
    matches = [b.get('id') for b in buildings if b.get('name') == building]
    if not matches:
        return None
    if len(matches) > 1:
        print(f"Found multiple buildings named {building} - ids = {matches} - please retry using an id")
        return None
    return matches[0]


def get_equipment(client, building_id):
    all_equipment = client.get_building_equipment(building_id)
    for e in all_equipment:
        if e['suffix'] == equip_suffix:
            return e
    return None


def fetch_time_series(api_key, building, equip_suffix, start_time, end_time):
    client = ProductionAPIClient(api_key=api_key)
    building_id = get_building_id(client, building)
    if building_id is None:
        print(f"Could not find a building named '{building}'")
        usage()

    equipment = get_equipment(client, building_id)
    if equipment is None:
        print(f"Could not find equipment with suffix '{equip_suffix}'")
        usage()

    point_ids = [p['id'] for p in equipment['points']]
    timeseries = client.query_point_timeseries(point_ids, start_time, end_time)

    return points_df_from_timeseries(timeseries, equipment['points'])


if __name__ == '__main__':
    api_key = os.environ.get('ONBOARD_API_KEY')
    if api_key is None:
        print("API key must be set as environment variable ONBOARD_API_KEY")
        sys.exit(1)

    if len(sys.argv) < 5:
        usage()
    building = sys.argv[1]
    equipment = sys.argv[2]
    start = sys.argv[3]
    end = sys.argv[4]

    if not building or not equipment:
        usage()
    split = equipment.split(' ')
    if len(split) == 1:
        equip_suffix = split[0]
    else:
        equip_suffix = split[1]

    df = fetch_time_series(api_key, building, equip_suffix, start, end)

    print(df.head(5))
    print(len(df))
