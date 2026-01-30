import boto3
import json
import os
from botocore.config import Config

def lambda_handler(event, context):
    s3 = boto3.client('s3', config=Config(signature_version='s3v4'))
    bucket_name = "audio-uploads-lpl-26"
    
    # Get filename from frontend request
    body = json.loads(event.get('body', '{}'))
    file_name = body.get('fileName', 'upload.mp3')

    # Generate the temporary upload URL
    presigned_url = s3.generate_presigned_url(
        ClientMethod='put_object',
        Params={'Bucket': bucket_name, 'Key': file_name},
        ExpiresIn=300
    )

    return {
        'statusCode': 200,
        'headers': {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Allow-Methods": "OPTIONS,POST"
        },
        'body': json.dumps({'uploadUrl': presigned_url})
    }