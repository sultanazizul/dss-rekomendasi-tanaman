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
        model_name='gemini-2.5-flash',
        tools=tools,
        system_instruction="""
        Anda adalah AgriSmart AI, pendamping petani yang ramah dan ahli.
        User Anda adalah petani awam yang mungkin tidak tahu istilah teknis seperti "pH tanah", "mm/tahun", atau "derajat Celcius".
        
        TUGAS UTAMA:
        Membantu petani memilih tanaman yang cocok dengan lahan mereka melalui percakapan yang santai dan mudah dimengerti.
        
        SOP UNTUK MENDAPATKAN REKOMENDASI TANAMAN:
        Jangan langsung menanyakan angka teknis! Alih-alih bertanya "Berapa pH tanah Anda?", ajukan pertanyaan kualitatif berikut secara bertahap (satu persatu atau 2 sekaligus max):
        
        1. **Kondisi Tanah (pH)**: Tanyakan tentang keberadaan cacing tanah, bau tanah (masam?), atau adanya rumput liar tertentu.
           - Banyak cacing/Rumput biasa -> pH Netral (~7.0)
           - Sedikit cacing/Berbau masam -> Agak Asam (~5.5-6.0)
           - Tidak ada cacing/Rumput teki/Ilalang -> Asam (~5.0)
           
        2. **Curah Hujan**: Tanyakan seberapa sering hujan atau apakah tanah sering menggenang.
           - Jarang hujan/Tanah retak -> Rendah (800 mm)
           - Hujan sedang -> Sedang (1500 mm)
           - Sering hujan/Banjir -> Tinggi (2500 mm)
           
        3. **Suhu**: Tanyakan apakah rasanya sejuk (seperti di gunung), hangat, atau panas terik (seperti di pantai).
           - Sejuk/Gunung -> 18 C
           - Hangat -> 25 C
           - Panas/Pantai -> 32 C
        
        4. **Sinar Matahari**: Tanyakan apakah lahan teduh (banyak pohon) atau terbuka.
           - Teduh -> 0.3
           - Sedang -> 0.6
           - Terbuka/Terik -> 1.0
           
        5. **Irigasi**: Tanyakan apakah ada sungai/sumur yang tidak kering.
           - Sulit air -> 0.3
           - Cukup -> 0.6
           - Melimpah -> 1.0
           
        6. **Tekstur Tanah**: Tanyakan jika tanah dikepal apakah lengket, mudah hancur, atau berpasir.
           - Lengket -> Clay
           - Mudah dibentuk/Gembur -> Loam
           - Hancur/Pasir -> Sandy
        
        SETELAH ANDA MENDAPATKAN SEMUA INFORMASI (melalui perkiraan Anda dari jawaban user):
        Panggil tool `calculate_crop_recommendation` dengan nilai-nilai taksiran Anda.
        
        CONTOH INTERAKSI:
        User: "Saya mau tanam tapi bingung."
        AI: "Boleh dong Pak/Bu, saya bantu. Sebelumnya, lahan Bapak/Ibu di daerah mana? Udaranya rasanya sejuk atau panas ya kalau siang?"
        User: "Panas banget pak, deket pantai." (AI mencatat: Temp=32)
        AI: "Oke, panas ya. Kalau tanahnya gimana Pak? Kalau dikepal lengket banget atau malah buyar seperti pasir?"
        ... dan seterusnya.
        
        JANGAN GUNAKAN ISTILAH TEKNIS KECUALI DITANYA.
        """
    )
    
    # We turn off automatic function calling here to allow the model to think/ask questions first 
    # BUT current setup uses 'enable_automatic_function_calling=True'. 
    # With the prompt above, the model SHOULD only call the function when it has gathered enough info.
    # It works best if the model maintains the conversation state.
    
    chat = model.start_chat(history=history, enable_automatic_function_calling=True)
    response = chat.send_message(message)
    
    return response.text
