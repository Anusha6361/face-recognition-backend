# app/schemas.py
from pydantic import BaseModel
from typing import List, Optional

class UserOut(BaseModel):
    id: int
    username: str
    email: str

    class Config:
        orm_mode = True

class FaceMatch(BaseModel):
    user_id: int
    score: float
    bbox: List[int]
    metadata: Optional[dict] = None

class WSMatchResponse(BaseModel):
    type: str
    frame_id: str
    matches: List[FaceMatch] = []
