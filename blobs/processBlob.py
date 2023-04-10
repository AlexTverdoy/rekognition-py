import json
import urllib.parse
import boto3


def lambda_handler(event, context):
    # print("Received event: " + json.dumps(event, indent=2))
    # TODO set up real profile name
    session = boto3.Session(profile_name='profile-name')
    client = session.client('rekognition')

    dynamodb = boto3.resource('dynamodb')
    client = boto3.client('dynamodb')
    # Getting the table Blobs object
    table_blobs = dynamodb.Table('Blobs')

    # Get the object from the event and show its content type
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    try:
        response = client.detect_labels(Image={'S3Object': {'Bucket': bucket, 'Name': key}},
                                        MaxLabels=10,
                                        Features=["GENERAL_LABELS"])

        table_blobs.update_item(
            Key={'blob_id': key},
            UpdateExpression='set labels = :l',
            ExpressionAttributeValues={
                ':l': json.dumps(response['Labels'], indent=2, default=str)},
        )

    except Exception as e:
        print(e)
        print('Error getting object {} from bucket {}. '
              'Make sure they exist and your bucket is in the same region as this function.'.format(key, bucket))
        raise e

