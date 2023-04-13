# ImageRekognition Service

## Requirements
* serverless
* aws account (set up credentials locally)

### How to use

Deploy project with 
```bash
sls deploy
```

ServerlessFramework will automatically deploy service to AWS with all related resources and triggers.

There are two endpoints available:
```
POST */blobs
GET */blobs/{blob_id}
```

1. Make POST request to /blobs. Payload:
```json
{
    "callback_url": {valid_callback_url}
}
```
Example response 
```json
{
    "blob_id": "e399fac6-d9e1-11ed-bc52-4d52e00c1d71",
    "callback_url": "https://webhook.site/708b8449-ac4a-4cce-a2da-ff04f68ef0c2",
    "upload_url": "https://image-rekognition-service-dev.s3.amazonaws.com/e399fac6-d9"
}
    
```
2. Rename blob file to 'blob_id' value name
3. Make PUT request to 'upload_url' with renamed blob attached to the request
4. Request to 'callback_url' should be triggered after the rekognition process ends
Expected payload:
```json
{
  "blob_id": "e399fac6-d9e1-11ed-bc52-4d52e00c1d71",
  "callback_url": "https://webhook.site/708b8449-ac4a-4cce-a2da-ff04f68ef0c2",
  "labels": [
    {
      "Name": "Animal",
      "Confidence": 99.61192321777344,
      "Instances": [],
      "Parents": [],
      "Aliases": [],
      "Categories": [
        {
          "Name": "Animals and Pets"
        }
      ]
    },
    {
      "Name": "Canine",
      "Confidence": 99.61192321777344,
      "Instances": [],
      "Parents": [
        {
          "Name": "Animal"
        },
        {
          "Name": "Mammal"
        }
      ],
      "Aliases": [],
      "Categories": [
        {
          "Name": "Animals and Pets"
        }
      ]
    }
  ]
}
```
5. Make GET request to /blobs/{blob_id}. Response should be the same as the payload from previous request
