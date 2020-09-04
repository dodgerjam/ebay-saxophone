from ebaysdk.shopping import Connection as shopping
import boto3
import pandas as pd
import io
from datetime import datetime, timedelta
import numpy as np
import yaml
import ebaysdk


class APIError(Exception):
    """An API Error Exception"""

    def __init__(self, response):
        self.response = response

    def __str__(self):
        return "APIError: error = {}".format(self.response.dict()['errorMessage']['error']['message'])

def nameValue2dict(nv):
    return {item['Name']:item['Value'] for item in nv}

class SpecificItemFinder():

    def __init__(self):
        s3_client = boto3.client('s3')
        obj = s3_client.get_object(Bucket = 'ebayfindingdata', Key = 'ebay.yaml')['Body']
        self.api = shopping(appid = yaml.load(obj)['open.api.ebay.com']['appid'], config_file=None)
        self.specifics = ['Brand', 'Type', 'Skill Level', 'Body Finish', 'Body Material', 'Key Finish', 'Custom Bundle', 'Modified Item', 'Modified Description', 'Country/Region of Manufacture']
        self.to_time = (datetime.now() + timedelta(days=1)).isoformat()
    
    def itemSpecificGetter(self, itemid):

        api_request = {
                'ItemID' : itemid,
                'IncludeSelector' : ['ItemSpecifics'],
                }

        try:
            response = self.api.execute('GetSingleItem', api_request)
        except ebaysdk.exception.ConnectionError:
            return None

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
        
        return df1.set_index('ItemID')


    def allItemSpecifics(self, itemIDs):
        return pd.concat([self.itemSpecificGetter(itemid) for itemid in itemIDs])

    def findSpecificItems(self):
        s3_client = boto3.client('s3')
        s3_resource = boto3.resource('s3')
        # bucket = s3.Bucket('ebayfindingdata')
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%m-%d-%Y")
        obj = s3_client.get_object(Bucket = 'ebayfindingdata', Key = 'finding/{}.csv'.format(yesterday))
        df = pd.read_csv(obj['Body'], index_col='itemId')
        itemIDs = df.index.values
        df1 = self.allItemSpecifics(itemIDs)

        s_buf = io.StringIO()

        df1.to_csv(s_buf)

        return s3_resource.Bucket('ebayfindingdata').put_object(Key='shopping/{}.csv'.format(yesterday), Body=s_buf.getvalue())

        # return df1.join(df).to_csv('data/shopping/{}.csv'.format(yesterday))    

def lambda_handler(event=None, context=None):
    sif = SpecificItemFinder()
    sif.findSpecificItems()   


