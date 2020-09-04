from ebaysdk.shopping import Connection as shopping
import boto3
import pandas as pd
import io
from datetime import datetime, timedelta
import numpy as np
import ebaysdk
import yaml

class APIError(Exception):
    """An API Error Exception"""

    def __init__(self, response):
        self.response = response

    def __str__(self):
        return "APIError: error = {}".format(self.response.dict()['errorMessage']['error']['message'])

def nameValue2dict(nv):
    return {item['Name']:item['Value'] for item in nv}

class ItemDescriptionFinder():

    def __init__(self):
        s3_client = boto3.client('s3')
        obj = s3_client.get_object(Bucket = 'ebayfindingdata', Key = 'ebay.yaml')['Body']
        self.api = shopping(appid = yaml.load(obj)['open.api.ebay.com']['appid'], config_file=None)
        self.specifics = ['Brand', 'Type', 'Skill Level', 'Body Finish', 'Body Material', 'Key Finish', 'Custom Bundle', 'Modified Item', 'Modified Description', 'Country/Region of Manufacture']
        self.to_time = (datetime.now() + timedelta(days=1)).isoformat()
    
    def itemDescriptionGetter(self, itemid):

        api_request = {
                'ItemID' : itemid,
                'IncludeSelector' : ['TextDescription'],
                }
        try:
            response = self.api.execute('GetSingleItem', api_request)
        except ebaysdk.exception.ConnectionError:
            return None
            

        if response.dict()['Ack'] == 'Failure':
            raise APIError(response)

        df1 = pd.json_normalize(response.dict()['Item'],  sep='-')
        
        return df1.set_index('ItemID')[['Description']]


    def allItemDescriptions(self, itemIDs):
        return pd.concat([self.itemDescriptionGetter(itemid) for itemid in itemIDs])

    def findItemDescriptions(self, yesterday = (datetime.now() - timedelta(days=1)).strftime("%m-%d-%Y")):
        s3_client = boto3.client('s3')
        s3_resource = boto3.resource('s3')

        obj = s3_client.get_object(Bucket = 'ebayfindingdata', Key = 'finding/{}.csv'.format(yesterday))
        df = pd.read_csv(obj['Body'], index_col='itemId')
        # df = pd.read_csv('data/finding/{}.csv'.format('08-10-2020'), index_col='itemId')
        itemIDs = df.index.values
        # itemIDs = df.index + [101010]

        df1 = self.allItemDescriptions(itemIDs)

        s_buf = io.StringIO()

        df1.to_csv(s_buf)

        return s3_resource.Bucket('ebayfindingdata').put_object(Key='descriptions/{}.csv'.format(yesterday), Body=s_buf.getvalue())

        # return df1.to_csv('data/descriptions/{}.csv'.format(yesterday))    

def lambda_handler(event=None, context=None):
    idf = ItemDescriptionFinder()
    idf.findItemDescriptions()   
