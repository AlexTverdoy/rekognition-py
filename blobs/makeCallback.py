import urllib3
import json


def make_callback(event, context):
    for record in event['Records']:
        # extract the necessary info from the DynamoDB stream record
        try:
            if record['eventName'] == 'MODIFY':
                new_image = record['dynamodb']['NewImage']

                callback_url = new_image['callback_url']['S']
                labels = new_image['labels']['S']

                item = {
                    'blob_id': new_image['blob_id']['S'],
                    'callback_url': callback_url,
                    'labels': json.loads(labels)
                }

                http = urllib3.PoolManager()

                # send a POST request to the callback URL with the blob as the payload
                response = http.request(
                    'POST',
                    callback_url,
                    headers={"Content-Type": "application/json"},
                    body=json.dumps(item).encode('utf-8'))

                # check the response status code and raise an error if necessary
                if response.status != 200:
                    raise ValueError('Failed to send message to callback URL')
        except Exception as e:
            print(e)
            print('Closing lambda function')
            raise e

    print('Successfully sent message to callback URL')
    return
