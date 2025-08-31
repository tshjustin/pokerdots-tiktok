import httpx
import asyncio
from database.session import SessionLocal
from database.models import Video
from ..storage.s3_client import s3_client, BUCKET_NAME

import os 

INFERENCE_SERVICE_URL = os.getenv("REGION_NAME")

async def trigger_analysis(video_id: int):
    asyncio.create_task(process_video_ai(video_id))

async def process_video_ai(video_id: int):
    db = SessionLocal()
    try:
        video = db.get(Video, video_id)
        if not video:
            return
        
        video.ai_status = "processing"
        db.commit()
        
        video_data = download_from_s3(video.s3_key)
        
        ai_result = await call_ai_service(video_data, video_id)
        
        video.ai_score = extract_confidence(ai_result["deepfake_result"])
        video.ai_label = determine_label(ai_result)
        video.genuinity_score = ai_result["genuinity"]
        video.ai_status = "completed"
        db.commit()
        
    except Exception as e:
        video.ai_status = "failed"
        db.commit()
        print(f"processing failed for video {video_id}: {e}")
    finally:
        db.close()

def download_from_s3(s3_key: str) -> bytes:
    response = s3_client.get_object(Bucket=BUCKET_NAME, Key=s3_key)
    return response['Body'].read()

async def call_ai_service(video_data: bytes, video_id: int):
    async with httpx.AsyncClient(timeout=300) as client:
        files = {"file": ("video.mp4", video_data, "video/mp4")}
        
        response = await client.post(INFERENCE_SERVICE_URL, files=files)
        response.raise_for_status()
        return response.json()

def extract_confidence(deepfake_result):
    if deepfake_result and len(deepfake_result) > 0:
        return deepfake_result[0].get('score', 0.0)
    return 0.0

def determine_label(ai_result):
    deepfake_result = ai_result.get("deepfake_result", [])
    if deepfake_result and len(deepfake_result) > 0:
        label = deepfake_result[0].get('label', 'UNKNOWN')
        return "FAKE" if label.upper() in ['FAKE', 'DEEPFAKE'] else "REAL"
    return "UNKNOWN"