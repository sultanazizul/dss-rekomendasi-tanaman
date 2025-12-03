from typing import List, Dict
from app.models import Question, QuestionOption

# Mapping configuration
# This maps the option code (A, B, C) to a numerical value or range representative
# For ranges, we might take the midpoint.

# Example mappings (Midpoints):
# pH: A (4.5-5.5) -> 5.0, B (5.5-6.5) -> 6.0, C (6.5-7.5) -> 7.0
# Rain (mm/year): A (<1000) -> 800, B (1000-2000) -> 1500, C (>2000) -> 2500
# Temp (C): A (Sejuk <20) -> 18, B (Sedang 20-30) -> 25, C (Panas >30) -> 32
# Sun: A (Redup) -> 0.3, B (Sedang) -> 0.6, C (Terik) -> 1.0
# Irrigation: A (Sulit) -> 0.3, B (Cukup) -> 0.6, C (Melimpah) -> 1.0
# Soil: A (Lempung/Clay) -> 'Clay', B (Gembur/Loam) -> 'Loam', C (Pasir/Sandy) -> 'Sandy'

VALUE_MAPPING = {
    "ph": {"A": 5.0, "B": 6.0, "C": 7.0},
    "rain": {"A": 800.0, "B": 1500.0, "C": 2500.0},
    "temp": {"A": 18.0, "B": 25.0, "C": 32.0},
    "sun": {"A": 0.3, "B": 0.6, "C": 1.0},
    "irrigation": {"A": 0.3, "B": 0.6, "C": 1.0},
    "soil": {"A": "Clay", "B": "Loam", "C": "Sandy"} # Special handling for categorical
}

QUESTIONS_DATA = [
    {
        "id": "q_ph",
        "text": "Bagaimana kondisi tanah Anda saat disentuh atau dicium baunya?",
        "category": "ph",
        "options": [
            {"label": "Berbau masam, tanah becek/gambut, banyak rumput teki", "value_code": "A", "description": "Indikasi tanah Asam (pH 4.5 - 5.5)"},
            {"label": "Tanah biasa, tidak berbau menyengat, warna coklat/hitam", "value_code": "B", "description": "Indikasi tanah Agak Asam - Netral (pH 5.5 - 6.5)"},
            {"label": "Tanah kering, kadang ada sisa kapur, tidak berbau", "value_code": "C", "description": "Indikasi tanah Netral - Basa (pH 6.5 - 7.5)"}
        ]
    },
    {
        "id": "q_rain",
        "text": "Seberapa sering hujan turun di daerah Anda dalam setahun?",
        "category": "rain",
        "options": [
            {"label": "Jarang hujan, sering kering", "value_code": "A", "description": "Curah hujan rendah (< 1000 mm/tahun)"},
            {"label": "Hujan sedang, ada musim kemarau dan hujan seimbang", "value_code": "B", "description": "Curah hujan sedang (1000 - 2000 mm/tahun)"},
            {"label": "Sering hujan hampir sepanjang tahun", "value_code": "C", "description": "Curah hujan tinggi (> 2000 mm/tahun)"}
        ]
    },
    {
        "id": "q_temp",
        "text": "Bagaimana suhu udara rata-rata di daerah Anda?",
        "category": "temp",
        "options": [
            {"label": "Sejuk / Dingin (Dataran Tinggi)", "value_code": "A", "description": "Suhu rata-rata < 20°C"},
            {"label": "Hangat / Sedang", "value_code": "B", "description": "Suhu rata-rata 20°C - 30°C"},
            {"label": "Panas (Dataran Rendah Pesisir)", "value_code": "C", "description": "Suhu rata-rata > 30°C"}
        ]
    },
    {
        "id": "q_sun",
        "text": "Seberapa banyak sinar matahari yang masuk ke lahan?",
        "category": "sun",
        "options": [
            {"label": "Sering mendung atau terhalang pohon/bangunan", "value_code": "A", "description": "Intensitas rendah"},
            {"label": "Cukup, ada panas dan teduh", "value_code": "B", "description": "Intensitas sedang"},
            {"label": "Sangat terik sepanjang hari", "value_code": "C", "description": "Intensitas tinggi"}
        ]
    },
    {
        "id": "q_irrigation",
        "text": "Bagaimana ketersediaan air untuk penyiraman?",
        "category": "irrigation",
        "options": [
            {"label": "Sulit air, hanya mengandalkan hujan", "value_code": "A", "description": "Ketersediaan rendah"},
            {"label": "Ada sumur atau sungai kecil", "value_code": "B", "description": "Ketersediaan sedang"},
            {"label": "Irigasi teknis lancar / dekat sumber air besar", "value_code": "C", "description": "Ketersediaan tinggi"}
        ]
    },
    {
        "id": "q_soil",
        "text": "Apa jenis tekstur tanah di lahan Anda?",
        "category": "soil",
        "options": [
            {"label": "Liat / Lempung (Lengket saat basah, keras saat kering)", "value_code": "A", "description": "Tanah Liat (Clay)"},
            {"label": "Gembur (Mudah dicangkul, remah)", "value_code": "B", "description": "Tanah Lempung Berpasir (Loam)"},
            {"label": "Berpasir (Kasar, air cepat meresap)", "value_code": "C", "description": "Tanah Pasir (Sandy)"}
        ]
    }
]

def get_questions() -> List[Question]:
    return [Question(**q) for q in QUESTIONS_DATA]

def map_answers_to_values(answers: List[Dict[str, str]]) -> Dict[str, any]:
    """
    Converts list of user answers [{'question_id': 'q_ph', 'selected_option': 'A'}, ...]
    to a dictionary of technical values {'ph': 5.0, ...}
    """
    result = {}
    # Create a lookup for question category by id
    q_lookup = {q['id']: q['category'] for q in QUESTIONS_DATA}
    
    for ans in answers:
        qid = ans.get('question_id')
        code = ans.get('selected_option')
        
        if qid in q_lookup:
            category = q_lookup[qid]
            if category in VALUE_MAPPING and code in VALUE_MAPPING[category]:
                result[category] = VALUE_MAPPING[category][code]
                
    return result
