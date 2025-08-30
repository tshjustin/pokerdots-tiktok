from pydantic import BaseModel, Field

class CreateUserRequest(BaseModel):
    username: str
    password: str
    email: str

class Token(BaseModel):
    access_token: str
    token_type: str

class Message(BaseModel):
    message: str = Field(..., example="User created")

class ErrorResponse(BaseModel):
    detail: str = Field(..., example="Username is already taken")