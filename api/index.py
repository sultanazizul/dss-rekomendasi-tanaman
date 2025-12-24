from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.ahp import AHPCalculator
from app.models import RecommendationResponse, Crop, Recommendation, UserInputSubmission, Question
from app.database import get_supabase_client
from app.mapping import get_questions, map_answers_to_values

app = FastAPI(title="Sistem Rekomendasi Tanaman AHP")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize AHP Calculator
ahp_calculator = AHPCalculator()

# --- Get Questions Endpoint ---
@app.get("/api/questions", response_model=List[Question])
async def get_questions_endpoint():
    return get_questions()

# --- Recommend Endpoint ---
@app.post("/api/recommend", response_model=RecommendationResponse)
async def get_recommendations(submission: UserInputSubmission):
    try:
        supabase = get_supabase_client()
        
        answers_dicts = [{"question_id": a.question_id, "selected_option": a.selected_option} for a in submission.answers]
        technical_values = map_answers_to_values(answers_dicts)
        
        print(f"Calculated Technical Values: {technical_values}")

        response = supabase.table('crops').select("*").execute()
        crops_data = response.data
        crops = [Crop(**item) for item in crops_data]
        
        if not crops:
            raise HTTPException(status_code=404, detail="No crops found in database")

        user_input_data = {
            "ph_value": technical_values.get('ph'),
            "rain_value": technical_values.get('rain'),
            "temp_value": technical_values.get('temp'),
            "sun_value": technical_values.get('sun'),
            "irrigation_value": technical_values.get('irrigation'),
            "soil_type": technical_values.get('soil')
        }
        try:
           supabase.table('user_inputs').insert(user_input_data).execute()
        except Exception as e:
           print(f"Warning: Failed to save user input to DB: {e}")
        
        recommendations = ahp_calculator.rank_crops(technical_values, crops)
        
        return RecommendationResponse(recommendations=recommendations)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/crops", response_model=List[Crop])
async def get_crops():
    try:
        supabase = get_supabase_client()
        response = supabase.table('crops').select("*").execute()
        return [Crop(**item) for item in response.data]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class ChatRequest(BaseModel):
    message: str
    history: List[dict] = []

@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    from app.ai import get_chat_response
    try:
        gemini_history = []
        for msg in request.history:
            role = "user" if msg['role'] == 'user' else "model"
            gemini_history.append({"role": role, "parts": [msg['content']]})
            
        response_text = get_chat_response(request.message, gemini_history)
        return {"response": response_text}
    except Exception as e:
        print(f"Chat Error: {e}")
        return {"response": "Maaf, terjadi kesalahan pada sistem AI. Pastikan API Key sudah benar."}

# Export for Vercel
handler = app
