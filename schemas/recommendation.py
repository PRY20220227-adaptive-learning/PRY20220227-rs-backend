from typing import Optional
from pydantic import BaseModel


class RecommendationCreate(BaseModel):
    date: str
    url: str
    topic: str
    user_id: int


class RecommendationUpdate(BaseModel):
    recommendation_id: int
    date: Optional[str]
    url: Optional[str]
    topic: Optional[str]
    user_id: Optional[int]


class Recommendation(RecommendationCreate):
    recommendation_id: int

    class Config:
        orm_mode = True


class RecommendationResponse(BaseModel):
    date: str
    url: str
    topic: str
