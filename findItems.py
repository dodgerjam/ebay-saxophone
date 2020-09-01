from ebaysdk.finding import Connection
import boto3
import pandas as pd
import io
from datetime import datetime, timedelta
import yaml

class APIError(Exception):
        """An API Error Exception"""

        def __init__(self, response):
                self.response = response

        def __str__(self):
                return "APIError: error = {}".format(self.response.dict()['errorMessage']['error']['message'])


class ItemFinder():

        def __init__(self):
                s3_client = boto3.client('s3')
                obj = s3_client.get_object(Bucket = 'ebayfindingdata', Key = 'ebay.yaml')['Body']
                appid = yaml.load(obj, Loader=yaml.FullLoader)['svcs.ebay.com']['appid']
                self.api = Connection(appid = appid, config_file=None, https=False, warnings=True)
                self.from_time = (datetime.now() - timedelta(days=2, minutes=10)).isoformat()
                self.to_time = (datetime.now() - timedelta(days=1, minutes=10)).isoformat()

        def api2df(self):
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
                        #{'name':'LocatedIn', 'value':'GB'},
                        {'name':'EndTimeFrom', 'value' : self.from_time},
                        {'name':'EndTimeTo', 'value' : self.to_time},
                        {'name':'HideDuplicateItems', 'value':'true'},
                        {'name':'MinPrice', 'value':100},

                        ],
                'paginationInput': {
                        'entriesPerPage': 100,
                        'pageNumber': 1},
                'sortOrder' : 'EndTimeSoonest'
                }

                response = self.api.execute('findCompletedItems', api_request)
                
                if response.dict()['ack'] == 'Failure':
                        raise APIError(response)

                print(response.dict()['paginationOutput'])

                totalPages = int(response.dict()['paginationOutput']['totalPages'])

                return pd.concat([self.requestPage2Df(pageNumber + 1) for pageNumber in range(totalPages)])

        def requestPage2Df(self, pageNumber):
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
                        #{'name':'LocatedIn', 'value':'GB'},
                        {'name':'EndTimeFrom', 'value' : self.from_time},
                        {'name':'EndTimeTo', 'value' : self.to_time},
                        {'name':'HideDuplicateItems', 'value':'true'},
                        {'name':'MinPrice', 'value':100},
                        ],
                'paginationInput': {
                        'entriesPerPage': 100,
                        'pageNumber': pageNumber},
                'sortOrder' : 'EndTimeSoonest'
                }
                response = self.api.execute('findCompletedItems', api_request)

                if response.dict()['ack'] == 'Failure':
                        raise APIError(response)

                df = pd.json_normalize(response.dict()['searchResult']['item'],  sep='-')

                return df.set_index('itemId')[['postalCode', 'location','sellerInfo-sellerUserName']]


        def findItems(self):
                # api = Connection(config_file = 'ebay.yaml')
                df = self.api2df()
                # return df.to_csv('data/finding/{}.csv'.format(datetime.now().strftime("%m-%d-%Y")))
                s3 = boto3.resource('s3')

                s_buf = io.StringIO()

                df.to_csv(s_buf)

                # return s3.Bucket('ebayfindingdata').put_object(Key='finding/{}.csv'.format(datetime.now().strftime("%m-%d-%Y")), Body=s_buf.getvalue())

                return df.to_csv('data/finding/{}.csv'.format(datetime.now().strftime("%m-%d-%Y")))

def lambda_handler(event=None, context=None):
        itemf = ItemFinder()
        itemf.findItems()

if __name__ == "__main__":
    lambda_handler()
