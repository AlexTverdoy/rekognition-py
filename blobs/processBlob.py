import json
import urllib.parse
import boto3
import os

dynamodb = boto3.resource('dynamodb')


def process(event, context):

    region_name = os.environ['REGION_NAME']

    rek_client = boto3.client('rekognition', region_name=region_name)

    # Getting the table object
    table_blobs = dynamodb.Table(os.environ['DYNAMODB_TABLE'])

    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    try:
        response = rek_client.detect_labels(Image={'S3Object': {'Bucket': bucket, 'Name': key}},
                                            MaxLabels=10,
                                            Features=["GENERAL_LABELS"])

        table_blobs.update_item(
            Key={'blob_id': key},
            UpdateExpression='set labels = :l',
            ExpressionAttributeValues={
                ':l': json.dumps(response['Labels'], default=str)},
        )

    except Exception as e:
        print(e)
        print('Error updating object in table. ')
        raise e

