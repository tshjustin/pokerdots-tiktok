from pydantic import BaseModel

class AdStartRequest(BaseModel):
    ad_id: int
    user_id: int

class AdStartResponse(BaseModel):
    session_token: str
    ad_duration: int
    message: str

class AdCompleteRequest(BaseModel):
    user_id: int
    session_token: str

class AdCompleteResponse(BaseModel):
    balance: int
    message: str