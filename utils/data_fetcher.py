"""
NOTE: THIS file is only and only for our utility and should NOT be submitted to MarkUs, as it is not
formatted properly.
"""

from typing import Any, Optional

import requests
from time import sleep
import geojson
import gzip


def fetch_data(url: str) -> Optional[dict]:
    response: requests.Response = requests.get(url)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print('Error:', response.status_code)
        return None


def main():
    object_ids_res = fetch_data('https://ws.lioservices.lrc.gov.on.ca/arcgis2/rest/services/'
                                'LIO_OPEN_DATA/LIO_Open09/MapServer/0/query?where=1%3D1&'
                                'outFields=*&returnIdsOnly=true&outSR=4326&f=json')
    object_ids: list[int] = object_ids_res['objectIds']

    object_ids_len: int = len(object_ids)

    print(f'Length of object_ids: {object_ids_len}')

    if object_ids_len == 0:
        raise WrongResException()

    object_ids.sort()
    max_object_id: int = object_ids[-1]

    cursor_begin_index: int = 0
    limit: int = 2000
    cursor_end_index: int = limit
    neg_inf: int = -100_000_000

    try:
        data: Optional[Any] = None

        while cursor_begin_index < object_ids_len:
            #  neg_inf to ensure that we don't miss any initial small ids
            cursor_begin: int = object_ids[cursor_begin_index] if cursor_begin_index > 0 else neg_inf

            # add 1 to max_object_id as we have less than in url where clause
            cursor_end: int = object_ids[cursor_end_index] if cursor_end_index < object_ids_len else max_object_id + 1
            print(f'Getting batch after value at object id index {cursor_begin_index}')

            draft_url: str = ('https://ws.lioservices.lrc.gov.on.ca/arcgis2/rest/services/LIO_OPEN_DATA/'
                              'LIO_Open09/MapServer/0/query?outFields=OGF_ID,FROM_JUNCTION_ID,TO_JUNCTION_ID,LENGTH,'
                              'DIRECTION_OF_TRAFFIC_FLOW,OBJECTID&returnGeometry=true&outSR=4326&f=json')
            url = f'{draft_url}&where=OBJECTID%20%3E%20{cursor_begin}%20AND%20OBJECTID%20%3C%20{cursor_end}'

            fetched_data = fetch_data(url)
            print(f'Got batch before value at object id index {cursor_end_index} (after start batch value)')

            if fetched_data is not None:
                if data is None:
                    data = fetched_data
                else:
                    data['features'].extend(fetched_data['features'])

                cursor_begin_index = cursor_end_index - 1
                cursor_end_index = cursor_begin_index + limit + 1  # add 1 as this is a terminate index
            else:
                raise WrongResException()

            print(f'Length of data so far {len(data['features'])}')
            sleep(0.01)

        features = data['features']
        print(f'Fetched total {len(features)}')

        object_ids_set: set = set(object_ids)
        assert len(object_ids_set) == len(object_ids)

        feature_object_id_set: set[int] = set([feature['attributes']['OBJECTID'] for feature in features])
        assert len(feature_object_id_set) == len(features)  # ensure no duplicates

        assert all(object_id in object_ids_set for object_id in feature_object_id_set)

        # code inspired from https://www.tutorialspoint.com/python/gzip_module.htm
        try:
            # mode "wt" taken from https://chatgpt.com/share/69c1d055-3954-8008-921d-be2138fafa22
            with gzip.open('../data/ontario_road_network.geojson.gz', 'wt') as f:
                f.write(geojson.dumps(data))
        except Exception as e:
            print(f'Exception occurred while writing to geojson file: {e}')

        # road_data_features: list = data['features']
        #
        # node_id: set[int] = set()
        # road_count: int = 0
        #
        # print(f'Length of roads: {len(road_data_features)}')
        # for road_data in road_data_features:
        #     attributes = road_data['attributes']
        #
        #     node_id.add(attributes['FROM_JUNCTION_ID'])
        #     node_id.add(attributes['TO_JUNCTION_ID'])
        #
        #     direction: str = attributes['DIRECTION_OF_TRAFFIC_FLOW']
        #
        #     if direction == 'Both':
        #         road_count += 2
        #     else:
        #         assert direction == 'Positive' or direction == 'Negative'
        #         road_count += 1
        #
        # print(f'Total unique nodes: {len(node_id)}')
        # print(f'Road count: {road_count}')

    except WrongResException:
        print('Error occurred while iteratively fetching api for getting roads data')


class WrongResException(Exception):
    def __str__(self):
        return 'Wrong URL Response.'


if __name__ == "__main__":
    main()
