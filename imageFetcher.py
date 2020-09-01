import pandas as pd
import ast
import io
import requests
import time
import boto3
from botocore.exceptions import ClientError


s3_client = boto3.client('s3')
s3_resource = boto3.resource('s3')

keys = [o['Key'] for o in s3_client.list_objects(Bucket = 'ebayfindingdata', Prefix = 'shopping')['Contents'] if '.csv' in o['Key']]

df = pd.concat([pd.read_csv(s3_client.get_object(Bucket = 'ebayfindingdata', Key = k)['Body'], index_col=0) for k in keys])
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
            time.sleep(1)
            response = requests.get(u)
            s3_resource.Bucket('ebayfindingdata').put_object(Key=f'images/{i}/{str(count).zfill(3)}.png', Body=response.content)
        time.sleep(1)
