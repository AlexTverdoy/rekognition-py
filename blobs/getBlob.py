import json
import boto3
import os

dynamodb = boto3.resource('dynamodb')


def get(event, context):

    blob_id = event['pathParameters']['id']
    # Getting the table object
    table_blobs = dynamodb.Table(os.environ['DYNAMODB_TABLE'])

    try:
        data = table_blobs.get_item(Key={'blob_id': blob_id})

        if 'Item' not in data:
            return {
                'statusCode': 404,
                'body': json.dumps('Blob not found')
            }
        labels = data['Item'].get('labels', '[]')

        item = {
            'blob_id': data['Item']['blob_id'],
            'callback_url': data['Item']['callback_url'],
            'labels': json.loads(labels)
        }

        return {
            'statusCode': 200,
            'body': json.dumps(item, default=str)
        }
    except Exception as e:
        print(e)
        print('Closing lambda function')
        return {
            'statusCode': 400,
            'body': json.dumps('Error getting the blob')
        }
