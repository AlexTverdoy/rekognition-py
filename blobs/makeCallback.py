import json
import boto3
import requests


def lambda_handler(event, context):
    for record in event['Records']:
        # extract the necessary info from the DynamoDB stream record
        if record['eventName'] == 'MODIFY':
            new_image = record['dynamodb']['NewImage']
            old_image = record['dynamodb']['OldImage']

            new_labels = new_image['labels']
            old_labels = old_image['labels']

            if new_labels == old_labels:
                return "The labels have not been changed"

            callback_url = new_image['callback_url']

            # send a POST request to the callback URL with the message as the payload
            headers = {'Content-type': 'application/json'}
            response = requests.post(callback_url, data=new_labels, headers=headers)

            # check the response status code and raise an error if necessary
            if response.status_code != 200:
                raise ValueError(f"Failed to send message to callback URL. Response status code: {response.status_code}")

    return "Successfully sent message to callback URL."
