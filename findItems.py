from ebaysdk.finding import Connection
import pandas as pd
from datetime import datetime, timedelta

class APIError(Exception):
    """An API Error Exception"""

    def __init__(self, response):
        self.response = response

    def __str__(self):
        return "APIError: error = {}".format(self.response.dict()['errorMessage']['error']['message'])


def api2df(from_time, to_time):
        api_request = {
        # 16231 - saxophones
        'categoryId': '16231',
        'keywords': 'sax',
        'outputSelector' : [
                        'SellerInfo',
                        'StoreInfo',
                ],
        'siteID' : 'EBAY-GB',
        'itemFilter' : [
                {'name':'LocatedIn', 'value':'GB'},
                {'name':'EndTimeFrom', 'value' : from_time},
                {'name':'EndTimeTo', 'value' :to_time},
                {'name':'HideDuplicateItems', 'value':'true'}
                ],
        'paginationInput': {
                'entriesPerPage': 100,
                'pageNumber': 1},
        'sortOrder' : 'EndTimeSoonest'
        }

        response = api.execute('findItemsByCategory', api_request)
        
        if response.dict()['ack'] == 'Failure':
                raise APIError(response)

        print(response.dict()['paginationOutput'])

        df = pd.json_normalize(response.dict()['searchResult']['item'],  sep='-')

        return df.set_index('itemId')[['postalCode', 'location']]


if __name__ == "__main__":
    api = Connection(config_file = 'ebay.yaml')
    from_time = datetime.now().isoformat()
    to_time =  (datetime.now() + timedelta(days=1)).isoformat()
    df = api2df(from_time, to_time)
    df.to_csv('data/finding/{}.csv'.format(datetime.now().strftime("%m-%d-%Y")))

