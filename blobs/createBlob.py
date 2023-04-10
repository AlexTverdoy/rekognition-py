import json
import boto3
import logging
import re
from botocore.exceptions import ClientError
from datetime import datetime
from uuid import uuid4


def create_presigned_post(bucket_name, object_name,
                          fields=None, conditions=None, expiration=3600):
    """Generate a presigned URL S3 POST request to upload a file

    :param bucket_name: string
    :param object_name: string
    :param fields: Dictionary of prefilled form fields
    :param conditions: List of conditions to include in the policy
    :param expiration: Time in seconds for the presigned URL to remain valid
    :return: Dictionary with the following keys:
        url: URL to post to
        fields: Dictionary of form fields and values to submit with the POST
    :return: None if error.
    """

    # Generate a presigned S3 POST URL
    s3_client = boto3.client('s3')
    try:
        response = s3_client.generate_presigned_post(bucket_name,
                                                     object_name,
                                                     Fields=fields,
                                                     Conditions=conditions,
                                                     ExpiresIn=expiration)
    except ClientError as e:
        logging.error(e)
        return None

    # The response contains the presigned URL and required fields
    return response


def lambda_handler(event, context):

    regex = re.compile(
        r'^(?:http|ftp)s?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

    callback_url = event['callback_url']
    if re.match(regex, callback_url) is None:
        return {
            'statusCode': 400,
            'body': json.dumps('Invalid callback url supplied')
        }

    # Instanciating connection objects with DynamoDB using boto3 dependency
    dynamodb = boto3.resource('dynamodb')
    client = boto3.client('dynamodb')

    # Getting the table Blobs object
    table_blobs = dynamodb.Table('Blobs')

    # Getting the current datetime and transforming it to string in the format bellow
    event_date_time = (datetime.now()).strftime("%Y-%m-%d %H:%M:%S")
    blob_id = uuid4()

    # Putting a try/catch to log to user when some error occurs
    try:
        # TODO what object_name should be set?
        object_name = 'OBJECT_NAME'
        # TODO how to set bucket name?
        response = create_presigned_post('BUCKET_NAME', object_name)
        if response is None:
            return {
                'statusCode': 400,
                'body': json.dumps('Error generating upload url')
            }

        table_blobs.put_item(
            Item={
                'event_date_time': event_date_time,
                'callback_url': callback_url,
                'blob_id': blob_id
            }
        )

        return {
            'statusCode': 200,
            'body': {
                'blob_id': blob_id,
                'callback_url': callback_url,
                # TODO should we add 'fields' as well?
                'upload_url': response['url']
            }
        }
    except:
        print('Closing lambda function')
        return {
            'statusCode': 400,
            'body': json.dumps('Error saving the blob')
        }
