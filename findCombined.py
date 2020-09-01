from ebaysdk.finding import Connection
from ebaysdk.shopping import Connection as shopping
import boto3
import pandas as pd
import io
from datetime import datetime, timedelta
import yaml
import numpy as np
from sqlalchemy.types import Integer, DateTime, Float, Boolean, DECIMAL
from sqlalchemy import create_engine


def nameValue2dict(nv):
    return {item['Name']:item['Value'] for item in nv}

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
        self.finding_api = Connection(appid = yaml.load(obj)['svcs.ebay.com']['appid'], config_file=None, Loader=yaml.FullLoader)
        obj = s3_client.get_object(Bucket = 'ebayfindingdata', Key = 'ebay.yaml')['Body']
        self.shopping_api =  shopping(appid = yaml.load(obj)['open.api.ebay.com']['appid'], config_file=None, Loader=yaml.FullLoader)
        self.from_time = (datetime.now() - timedelta(days=2, minutes=10)).isoformat()
        self.to_time = (datetime.now() - timedelta(days=1, minutes=10)).isoformat()
        self.specifics = ['Brand', 'Type', 'Skill Level', 'Body Finish', 'Body Material', 'Key Finish', 'Custom Bundle', 'Modified Item', 'Modified Description', 'Country/Region of Manufacture']
        self.columns = ['EndTime', 'StartTime',
       'ViewItemURLForNaturalSearch', 'ListingType', 'Location',
       'GalleryURL', 'PictureURL', 'PostalCode',
       'Quantity', 'BidCount',
       'ListingStatus', 'QuantitySold',
       'TimeLeft', 'Title', 'HitCount',
       'Country',
       'ConditionDisplayName',
       'Seller-UserID', 'Seller-FeedbackRatingStar',
       'Seller-FeedbackScore', 'Seller-PositiveFeedbackPercent',
       'ConvertedCurrentPrice-_currencyID', 'ConvertedCurrentPrice-value',
       'CurrentPrice-_currencyID', 'CurrentPrice-value',
       'ItemSpecifics-Brand', 'ItemSpecifics-Type',
       'ItemSpecifics-Skill Level', 'ItemSpecifics-Body Finish',
       'ItemSpecifics-Body Material', 'ItemSpecifics-Key Finish',
       'ItemSpecifics-Custom Bundle', 'ItemSpecifics-Modified Item',
       'ItemSpecifics-Modified Description',
       'ItemSpecifics-Country/Region of Manufacture',
       'MinimumToBid-_currencyID', 'MinimumToBid-value', 'SKU',
       'Seller-TopRatedSeller',
       'BuyItNowAvailable',
       'BuyItNowPrice-_currencyID', 'BuyItNowPrice-value',
       'ConvertedBuyItNowPrice-_currencyID',
       'ConvertedBuyItNowPrice-value',
       'ConditionDescription', 
       # 'Subtitle',
       'Description']

        '''
        self.dtypes = {'EndTime':DateTime(), 'StartTime':DateTime(), 'Quantity':Integer(), 'BidCount':Integer(),
            'QuantitySold':Integer(),
            'HitCount':Integer(),
            'QuantitySoldByPickupInStore':Integer(),
            'Seller-FeedbackScore':Integer(), 
            #'Seller-PositiveFeedbackPercent':DECIMAL(1),
            #'ConvertedCurrentPrice-value':DECIMAL(2),
            #'CurrentPrice-value':DECIMAL(2),
            #'MinimumToBid-value':DECIMAL(2),
            'Seller-TopRatedSeller':Boolean(),
            'BuyItNowAvailable':Boolean(),
            #'BuyItNowPrice-value':DECIMAL(2),
            'ConvertedBuyItNowPrice-value':Float()}
        '''


    def getItemIDs(self):
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

        response = self.finding_api.execute('findCompletedItems', api_request)
        
        if response.dict()['ack'] == 'Failure':
                raise APIError(response)

        print(response.dict()['paginationOutput'])

        totalPages = int(response.dict()['paginationOutput']['totalPages'])

        return pd.concat([self.getItemIDsPages(pageNumber + 1) for pageNumber in range(totalPages)])

    def getItemIDsPages(self, pageNumber):
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
        response = self.finding_api.execute('findCompletedItems', api_request)

        if response.dict()['ack'] == 'Failure':
                raise APIError(response)

        df = pd.json_normalize(response.dict()['searchResult']['item'],  sep='-')

        return df.set_index('itemId')[['postalCode', 'location','sellerInfo-sellerUserName']]


    def findItems(self):
        # api = Connection(config_file = 'ebay.yaml')
        df = self.getItemIDs()
        # return df.to_csv('data/finding/{}.csv'.format(datetime.now().strftime("%m-%d-%Y")))
        s3 = boto3.resource('s3')

        s_buf = io.StringIO()

        df.to_csv(s_buf)

        # return s3.Bucket('ebayfindingdata').put_object(Key='finding/{}.csv'.format(datetime.now().strftime("%m-%d-%Y")), Body=s_buf.getvalue())

        # return df.to_csv('data/finding/{}.csv'.format(datetime.now().strftime("%m-%d-%Y")))

        return df


    def itemDetailsGetter(self, itemid):

        api_request = {
                'ItemID' : itemid,
                'IncludeSelector' : ['Details'],
                }

        response = self.shopping_api.execute('GetSingleItem', api_request)

        if response.dict()['Ack'] == 'Failure':
            raise APIError(response)

        df1 = pd.json_normalize(response.dict()['Item'],  sep='-')

        return df1.set_index('ItemID')


    def allItemDetails(self, itemIDs):
        return pd.concat([self.itemDetailsGetter(itemid) for itemid in itemIDs])

    def itemDescriptionGetter(self, itemid):

        api_request = {
                # 16231 - saxophones
                'ItemID' : itemid,
                'IncludeSelector' : 'TextDescription',
                }

        response = self.shopping_api.execute('GetSingleItem', api_request)

        if response.dict()['Ack'] == 'Failure':
            raise APIError(response)

        df1 = pd.json_normalize(response.dict()['Item'],  sep='-')

        return df1.set_index('ItemID')[['Description']]

    def allItemDescriptions(self, itemIDs):
        return pd.concat([self.itemDescriptionGetter(itemid) for itemid in itemIDs])


    def itemSpecificGetter(self, itemid):

        api_request = {
                'ItemID' : itemid,
                'IncludeSelector' : ['ItemSpecifics'],
                }

        response = self.shopping_api.execute('GetSingleItem', api_request)

        if response.dict()['Ack'] == 'Failure':
            raise APIError(response)

        df1 = pd.json_normalize(response.dict()['Item'],  sep='-')

        if 'ItemSpecifics-NameValueList' in df1.columns:
            df1['ItemSpecifics'] = df1['ItemSpecifics-NameValueList'].apply(nameValue2dict)

            df1 = df1.drop('ItemSpecifics-NameValueList', axis=1)

            for s in self.specifics:
                if s in df1['ItemSpecifics'].loc[0]:
                    df1['ItemSpecifics-{}'.format(s)] = df1['ItemSpecifics'].loc[0][s]
                else:
                    df1['ItemSpecifics-{}'.format(s)] = np.nan
        
        else: 
            for s in self.specifics:           
                df1['ItemSpecifics-{}'.format(s)] = np.nan
        
        return df1.set_index('ItemID')[['ItemSpecifics-{}'.format(s) for s in self.specifics]]

    def allItemSpecifics(self, itemIDs):
        return pd.concat([self.itemSpecificGetter(itemid) for itemid in itemIDs])


    def findSpecificItems(self):
        s3_client = boto3.client('s3')
        s3_resource = boto3.resource('s3')
        # bucket = s3.Bucket('ebayfindingdata')
        df = self.findItems()

        itemIDs = df.index.values
        #print(itemIDs)
        df1 = self.allItemDetails(itemIDs)

        df2 = self.allItemDescriptions(itemIDs)

        df3 = self.allItemSpecifics(itemIDs)

        print(df1.columns)
        print(df2.columns)
        print(df3.columns)


        s_buf = io.StringIO()

        df = pd.concat([df1, df2, df3], axis=1)

        print(df.columns)

        df = df[self.columns].reset_index().rename(columns={'index':'ItemID'})

        df['EndTime'] = pd.to_datetime(df['EndTime'])
        df['StartTime'] = pd.to_datetime(df['StartTime'])
        df['PictureURL'] = df['PictureURL'].apply(', '.join)
        df['Seller-TopRatedSeller'] = df['Seller-TopRatedSeller'].fillna(False).replace({'true':True}).astype(int)
        df['BuyItNowAvailable'] = df['BuyItNowAvailable'].fillna(False).replace({'true':True}).astype(int)

        engine = create_engine('mysql://root@localhost/ebaysax')

        df.to_sql('ebaysaxtable', engine, 
        #dtype = self.dtypes, 
        if_exists = 'append')

        # return s3_resource.Bucket('ebayfindingdata').put_object(Key='shopping/{}.csv'.format(yesterday), Body=s_buf.getvalue())

        return df.to_csv('data/shopping/{}.csv'.format('combined1'))    

def lambda_handler(event=None, context=None):
    itemf = ItemFinder()
    itemf.findSpecificItems()

if __name__ == "__main__":
    lambda_handler()
