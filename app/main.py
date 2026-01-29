from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os

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

# --- NEW: Get Questions Endpoint ---
@app.get("/api/questions", response_model=List[Question])
async def get_questions_endpoint():
    return get_questions()

# --- UPDATED: Recommend Endpoint accepts UserInputSubmission (List of Answers) ---
@app.post("/api/recommend", response_model=RecommendationResponse)
async def get_recommendations(submission: UserInputSubmission):
    try:
        supabase = get_supabase_client()
        
        # 1. Map Answers to Technical Values
        # submission.answers is a List[UserAnswer]
        # We need to convert it to list of dicts for our mapping function or just pass it if adapted
        answers_dicts = [{"question_id": a.question_id, "selected_option": a.selected_option} for a in submission.answers]
        
        # Values will be like {'ph': 6.5, 'rain': 1500, ...}
        technical_values = map_answers_to_values(answers_dicts)
        
        print(f"Calculated Technical Values: {technical_values}")

        # 2. Fetch Crops from DB
        response = supabase.table('crops').select("*").execute()
        crops_data = response.data
        
        # Convert to Crop objects
        crops = [Crop(**item) for item in crops_data]
        
        if not crops:
            raise HTTPException(status_code=404, detail="No crops found in database")

        # 3. Save User Input (Simplified: Saving the calculated values for analysis)
        # Ideally we should also save the raw answers in a separate table 'user_answers'
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
           # Don't fail the whole request just because tracking failed
        
        # 4. Calculate rankings
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
        # Convert history format if needed, for now passing as is (Gemini expects specific format)
        # Simplified: We'll let the frontend manage history context or just pass the message
        # Ideally, we should map the history to Gemini's Content object
        
        # For this prototype, we'll just pass the message and let Gemini handle the session in a real app
        # But here we are re-creating the chat object every time.
        # To support history properly with the stateless API, we need to map the history.
        
        # Mapping history (Simple version)
        gemini_history = []
        for msg in request.history:
            role = "user" if msg['role'] == 'user' else "model"
            gemini_history.append({"role": role, "parts": [{"text": msg['content']}]})
            
        response_text = get_chat_response(request.message, gemini_history)
        return {"response": response_text}
    except Exception as e:
        print(f"Chat Error: {e}")
        return {"response": "Maaf, terjadi kesalahan pada sistem AI. Pastikan API Key sudah benar."}

# Mount static files - MUST be last
if not os.path.exists("static"):
    os.makedirs("static")

app.mount("/", StaticFiles(directory="static", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
