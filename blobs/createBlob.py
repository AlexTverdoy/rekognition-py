import json
import boto3
import os
import re
from botocore.exceptions import ClientError
from datetime import datetime
from uuid import uuid1

dynamodb = boto3.resource('dynamodb')


def create(event, context):

    regex = re.compile(
        r'^(?:http|ftp)s?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

    data = json.loads(event['body'])
    callback_url = data['callback_url']

    if re.match(regex, callback_url) is None:
        return {
            'statusCode': 400,
            'body': json.dumps('Invalid callback url')
        }

    # Getting the table object
    table_blobs = dynamodb.Table(os.environ['DYNAMODB_TABLE'])

    s3_client = boto3.client('s3')

    # Getting the current datetime and transforming it to string in the format bellow
    event_date_time = (datetime.now()).strftime("%Y-%m-%d %H:%M:%S")
    blob_id = uuid1()

    try:
        presigned_url = s3_client.generate_presigned_url(
            ClientMethod='put_object',
            Params={
                'Bucket': os.environ['S3_BLOB_BUCKET'],
                'Key': str(blob_id)
            })

    except ClientError as e:
        print(e)
        print('Closing lambda function')
        return {
            'statusCode': 400,
            'body': json.dumps('Error generating upload url')
        }

    try:

        table_blobs.put_item(
            Item={
                'blob_id': str(blob_id),
                'callback_url': callback_url,
                'event_date_time': event_date_time
            }
        )

        return {
            'statusCode': 201,
            'body': json.dumps({
                'blob_id': str(blob_id),
                'callback_url': callback_url,
                'upload_url': presigned_url
            },
                default=str)
        }
    except Exception as e:
        print(e)
        print('Closing lambda function')
        return {
            'statusCode': 400,
            'body': json.dumps('Error saving the blob')
        }
