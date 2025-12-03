from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os

from app.ahp import AHPCalculator
from app.models import RecommendationResponse, Crop, Recommendation
from app.database import get_supabase_client

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

class UserInput(BaseModel):
    ph: float
    rain: float
    temp: float
    sun: float # 0.0 - 1.0
    irrigation: float # 0.0 - 1.0
    soil: str

@app.post("/api/recommend", response_model=RecommendationResponse)
async def get_recommendations(user_input: UserInput):
    try:
        supabase = get_supabase_client()
        
        # 1. Fetch Crops from DB
        response = supabase.table('crops').select("*").execute()
        crops_data = response.data
        
        # Convert to Crop objects
        crops = [Crop(**item) for item in crops_data]
        
        if not crops:
            raise HTTPException(status_code=404, detail="No crops found in database")

        # 2. Save User Input (Async/Fire-and-forget ideally, but here synchronous is fine)
        user_input_data = {
            "ph_value": user_input.ph,
            "rain_value": user_input.rain,
            "temp_value": user_input.temp,
            "sun_value": user_input.sun,
            "irrigation_value": user_input.irrigation,
            "soil_type": user_input.soil
        }
        supabase.table('user_inputs').insert(user_input_data).execute()
        
        # 3. Calculate rankings
        # Convert Pydantic model to dict for AHP
        input_dict = user_input.dict()
        recommendations = ahp_calculator.rank_crops(input_dict, crops)
        
        return RecommendationResponse(recommendations=recommendations)
    except Exception as e:
        print(f"Error: {e}")
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
            gemini_history.append({"role": role, "parts": [msg['content']]})
            
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
