from pydantic import BaseModel, Field
from typing import Optional

class ReplyRequest(BaseModel):
    platform: str
    post_text: str

class ReplyResponse(BaseModel):
    platform: str
    post_text: str
    generated_reply: str  
    timestamp: str

class DBReply(ReplyResponse):
    id: Optional[str] = Field(None, alias="_id")


