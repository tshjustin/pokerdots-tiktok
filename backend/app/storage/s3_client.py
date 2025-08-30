from fastapi import HTTPException

import uuid
import boto3

import os
from typing import IO

BUCKET_NAME = os.getenv("BUCKET_NAME", "your-videos-demo")
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")
AWS_REGION = os.getenv("REGION_NAME")


s3_client = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name='AWS_REGION'
)

async def upload_video_to_s3(file_content: bytes, filename, user_id):
    """
    Upload video to S3 & return s3 key
    
    """
    try:
        # unqiue s3 key --> user_id/{unique_hash}
        file_extension = filename.split('.')[-1]
        s3_key = f"videos/{user_id}/{uuid.uuid4()}.{file_extension}"
        
        # upload 
        s3_client.put_object(
            Bucket=BUCKET_NAME,
            Key=s3_key,
            Body=file_content,
            ContentType=f"video/{file_extension}"
        )
        
        return s3_key
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"s3 upload failed: {str(e)}")

def generate_presigned_url(s3_key, expiration = 3600):
    """
    generate presigned URL for video access

    TODO: Change the expiration timer if needed 
    """
    try:
        url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': BUCKET_NAME, 'Key': s3_key},
            ExpiresIn=expiration
        )
        return url
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"URL generation failed: {str(e)}")