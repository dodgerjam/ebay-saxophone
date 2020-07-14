from ebaysdk.shopping import Connection as shopping
import pandas as pd
from datetime import datetime, timedelta
import numpy as np
 
shop_api = shopping(config_file = 'ebay.yaml')

specifics = ['Brand', 'Type', 'Skill Level', 'Body Finish', 'Body Material', 'Key Finish', 'Custom Bundle', 'Modified Item', 'Modified Description', 'Country/Region of Manufacture']


class APIError(Exception):
    """An API Error Exception"""

    def __init__(self, response):
        self.response = response

    def __str__(self):
        return "APIError: error = {}".format(self.response.dict()['errorMessage']['error']['message'])

def nameValue2dict(nv):
    return {item['Name']:item['Value'] for item in nv}


def itemSpecificGetter(itemid):

    api_request = {
            'ItemID' : itemid,
            'IncludeSelector' : ['ItemSpecifics'],
            }

    response = shop_api.execute('GetSingleItem', api_request)

    if response.dict()['Ack'] == 'Failure':
        raise APIError(response)

    df1 = pd.io.json.json_normalize(response.dict()['Item'],  sep='-')

    if 'ItemSpecifics-NameValueList' in df1.columns:
        df1['ItemSpecifics'] = df1['ItemSpecifics-NameValueList'].apply(nameValue2dict)

        df1 = df1.drop('ItemSpecifics-NameValueList', axis=1)

        for s in specifics:
            if s in df1['ItemSpecifics'].loc[0]:
                df1['ItemSpecifics-{}'.format(s)] = df1['ItemSpecifics'].loc[0][s]
            else:
                df1['ItemSpecifics-{}'.format(s)] = np.nan
    
    else: 
         for s in specifics:           
            df1['ItemSpecifics-{}'.format(s)] = np.nan
    
    return df1.set_index('ItemID')


def allItemSpecifics(itemIDs):
    return pd.concat([itemSpecificGetter(itemid) for itemid in itemIDs])

if __name__ == "__main__":
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%m-%d-%Y")
    df = pd.read_csv('data/finding/{}.csv'.format(yesterday), index_col='itemId')
    itemIDs = df.index.values
    df1 = allItemSpecifics(itemIDs)
    df1.join(df).to_csv('data/shopping/{}.csv'.format(yesterday))    
