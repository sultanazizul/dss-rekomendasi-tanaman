import os
import google.generativeai as genai
from google.generativeai.types import FunctionDeclaration, Tool
from app.ahp import AHPCalculator
from app.database import get_supabase_client
from app.models import Crop

# Initialize AHP
ahp_calculator = AHPCalculator()

def calculate_crop_recommendation(ph: float, rain: float, temp: float, sun: float, irrigation: float, soil: str):
    """
    Calculates crop recommendations based on land parameters using AHP.
    
    Args:
        ph: Soil pH level (0-14).
        rain: Annual rainfall in mm.
        temp: Average temperature in Celsius.
        sun: Sun intensity (0.0 to 1.0). Low=0.3, Medium=0.6, High=1.0.
        irrigation: Irrigation availability (0.0 to 1.0). Low=0.3, Medium=0.6, High=1.0.
        soil: Soil type ('Clay', 'Sandy', 'Loam', 'Silt').
    """
    try:
        # Fetch crops from DB
        supabase = get_supabase_client()
        response = supabase.table('crops').select("*").execute()
        crops_data = response.data
        crops = [Crop(**item) for item in crops_data]
        
        if not crops:
            return "Error: No crops found in database."

        user_input = {
            "ph": ph,
            "rain": rain,
            "temp": temp,
            "sun": sun,
            "irrigation": irrigation,
            "soil": soil
        }
        
        recommendations = ahp_calculator.rank_crops(user_input, crops)
        
        # Format the output for the AI
        result_str = "Top Recommendations:\n"
        for i, rec in enumerate(recommendations[:3]): # Top 3
            result_str += f"{i+1}. {rec.crop_name} (Score: {rec.score:.4f})\n"
            
        return result_str
    except Exception as e:
        return f"Error calculating recommendations: {str(e)}"

def get_available_crops():
    """
    Retrieves the list of all available crops in the database along with their detailed growth requirements.
    Use this when the user asks what crops are supported, or asks for specific parameters of a crop (e.g. "What is the pH for rice?").
    """
    try:
        supabase = get_supabase_client()
        response = supabase.table('crops').select("*").execute()
        crops = response.data
        
        if not crops:
            return "No crops found in database."
            
        result_str = "Available Crops and Parameters:\n"
        for crop in crops:
            result_str += f"--- {crop['name']} ---\n"
            result_str += f"Description: {crop['description']}\n"
            result_str += f"pH Range: {crop['ph_min']} - {crop['ph_max']}\n"
            result_str += f"Rainfall: {crop['rain_min']} - {crop['rain_max']} mm/year\n"
            result_str += f"Temperature: {crop['temp_min']} - {crop['temp_max']} C\n"
            result_str += f"Sun Requirement: {crop['sun_requirement']}\n"
            result_str += f"Irrigation Need: {crop['irrigation_need']}\n"
            result_str += f"Soil Type: {crop['soil_type']}\n\n"
            
        return result_str
    except Exception as e:
        return f"Error fetching crops: {str(e)}"

# Configure Gemini
def get_chat_response(message: str, history: list = []):
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return "Error: GEMINI_API_KEY not found in environment variables."
        
    genai.configure(api_key=api_key)
    
    # Define the tool
    tools = [calculate_crop_recommendation, get_available_crops]
    
    model = genai.GenerativeModel(
        model_name='gemini-2.0-flash',
        tools=tools,
        system_instruction="""
        Anda adalah AgriSmart AI, konsultan pertanian ahli.
        Tujuan Anda adalah membantu petani dengan menjawab pertanyaan dan memberikan rekomendasi tanaman.
        
        INSTRUKSI PENTING:
        1. SELALU gunakan Bahasa Indonesia yang sopan dan mudah dimengerti.
        2. Jika user bertanya tentang tanaman apa saja yang tersedia ATAU bertanya tentang detail parameter tanaman tertentu (misal: "Apa parameter untuk Padi?"), gunakan tool `get_available_crops`.
        3. Jika user meminta rekomendasi tanaman untuk lahan mereka:
           - Tanyakan detail berikut jika belum diberikan: pH tanah, Curah Hujan (mm/tahun), Suhu (C), Intensitas Matahari (Rendah/Sedang/Tinggi), Irigasi (Rendah/Sedang/Tinggi), dan Jenis Tanah (Liat/Berpasir/Gembur/Endapan).
           - Konversi input Matahari/Irigasi ke angka: Rendah=0.3, Sedang=0.6, Tinggi=1.0.
           - Konversi input Jenis Tanah ke Bahasa Inggris untuk tool: Liat=Clay, Berpasir=Sandy, Gembur=Loam, Endapan=Silt.
           - Gunakan tool `calculate_crop_recommendation`.
        4. Jelaskan hasil rekomendasi dengan alasan mengapa tanaman tersebut cocok berdasarkan data yang diberikan.
        """
    )
    
    chat = model.start_chat(history=history, enable_automatic_function_calling=True)
    response = chat.send_message(message)
    
    return response.text
