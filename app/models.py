from pydantic import BaseModel
from typing import List, Optional, Dict

class QuestionOption(BaseModel):
    label: str
    value_code: str # 'A', 'B', 'C'
    description: str

class Question(BaseModel):
    id: str
    text: str
    category: str # 'ph', 'rain', 'temp', 'sun', 'irrigation', 'soil'
    options: List[QuestionOption]

class UserAnswer(BaseModel):
    question_id: str
    selected_option: str # 'A', 'B', 'C'

class UserInputSubmission(BaseModel):
    answers: List[UserAnswer]

class MatchDetails(BaseModel):
    ph: float
    rain: float
    temp: float
    sun: float
    irrigation: float
    soil: float

class Recommendation(BaseModel):
    crop_name: str
    score: float
    match_details: MatchDetails

class RecommendationResponse(BaseModel):
    recommendations: List[Recommendation]

class Crop(BaseModel):
    id: str
    name: str
    ph_min: float
    ph_max: float
    rain_min: float
    rain_max: float
    temp_min: float
    temp_max: float
    sun_requirement: str
    soil_type: str
    irrigation_need: str
    description: Optional[str] = None
