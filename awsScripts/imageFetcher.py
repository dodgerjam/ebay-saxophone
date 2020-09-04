import pandas as pd
import ast
import io
import requests
import time
import boto3
from botocore.exceptions import ClientError
from datetime import datetime, timedelta



s3_client = boto3.client('s3')
s3_resource = boto3.resource('s3')
yesterday = (datetime.now() - timedelta(days=3)).strftime("%m-%d-%Y")
obj = s3_client.get_object(Bucket = 'ebayfindingdata', Key = 'shopping/{}.csv'.format(yesterday))
df = pd.read_csv(obj['Body'], index_col='ItemID')
df = df[(~df.index.duplicated()) & (~df.PictureURL.isna())]
items = df.index.values
for i in items: 

    try:
        s3_client.get_object(Bucket = 'ebayfindingdata', Key = f'images/{i}/000.png')
        print(f'Skipping {i}')
    except ClientError:
        print(f'Fetching {i}')
        urls = ast.literal_eval(df.loc[i, 'PictureURL'])
        for count, u in enumerate(urls):
            response = requests.get(u)
            s3_resource.Bucket('ebayfindingdata').put_object(Key=f'images/{i}/{str(count).zfill(3)}.png', Body=response.content)
