from typing import List, Dict, Union
from app.models import Question, QuestionOption
import statistics

# Konfigurasi Pemetaan Nilai
# Kita menyematkan nilai numerik/teknis langsung ke dalam opsi jawaban ('value') 
# agar mudah dirata-rata.

QUESTIONS_DATA = [
    # ---------------------------------------------------------
    # 1. pH Tanah (3 Pertanyaan)
    # ---------------------------------------------------------
    {
        "id": "q_ph_1",
        "text": "Apakah banyak ditemukan cacing tanah saat Anda menggali lahan?",
        "category": "ph",
        "options": [
            {"label": "Ya, sangat banyak cacing", "value_code": "A", "description": "Tanah subur/netral (pH ~7.0)"},
            {"label": "Ada, tapi sedikit", "value_code": "B", "description": "Agak asam (pH ~6.0)"},
            {"label": "Tidak ada sama sekali", "value_code": "C", "description": "Kemungkinan asam (pH ~5.0)"}
        ],
        "values": {"A": 7.0, "B": 6.0, "C": 5.0}
    },
    {
        "id": "q_ph_2",
        "text": "Bagaimana aroma tanah Anda saat dicium??",
        "category": "ph",
        "options": [
            {"label": "Berbau masam atau menyengat", "value_code": "A", "description": "Indikasi tanah Asam (pH ~4.5 - 5.5)"},
            {"label": "Berbau tanah biasa (segar)", "value_code": "B", "description": "Indikasi tanah Netral (pH ~6.0 - 7.0)"},
            {"label": "Tidak berbau", "value_code": "C", "description": "Netral cenderung basa (pH ~7.0)"}
        ],
        "values": {"A": 5.0, "B": 6.5, "C": 7.0}
    },
    {
        "id": "q_ph_3",
        "text": "Apakah lahan banyak ditumbuhi tanaman liar seperti ilalang atau rumput teki?",
        "category": "ph",
        "options": [
            {"label": "Ya, dominan ilalang/rumput teki", "value_code": "A", "description": "Tanah cenderung Asam (pH ~5.0)"},
            {"label": "Ada rumput biasa, beragam", "value_code": "B", "description": "Tanah Agak Asam - Netral (pH ~6.0)"},
            {"label": "Jarang ada rumput liar", "value_code": "C", "description": "Tanah Netral (pH ~7.0)"}
        ],
        "values": {"A": 5.0, "B": 6.0, "C": 7.0}
    },

    # ---------------------------------------------------------
    # 2. Curah Hujan (2 Pertanyaan)
    # ---------------------------------------------------------
    {
        "id": "q_rain_1",
        "text": "Seberapa sering hujan turun di daerah Anda dalam seminggu terakhir (saat musim tanam)?",
        "category": "rain",
        "options": [
            {"label": "Jarang (1-2 kali atau kurang)", "value_code": "A", "description": "Curah hujan rendah (~800 mm/th)"},
            {"label": "Sedang (3-4 kali)", "value_code": "B", "description": "Curah hujan sedang (~1500 mm/th)"},
            {"label": "Sering (Hampir tiap hari)", "value_code": "C", "description": "Curah hujan tinggi (~2500 mm/th)"}
        ],
        "values": {"A": 800.0, "B": 1500.0, "C": 2500.0}
    },
    {
        "id": "q_rain_2",
        "text": "Setelah hujan deras, bagaimana kondisi air di lahan?",
        "category": "rain",
        "options": [
            {"label": "Cepat kering, tanah jadi retak", "value_code": "A", "description": "Indikasi kurang air"},
            {"label": "Lembab cukup lama tapi tidak menggenang", "value_code": "B", "description": "Kondisi ideal"},
            {"label": "Menggenang lama (banjir)", "value_code": "C", "description": "Indikasi kelebihan air"}
        ],
        "values": {"A": 800.0, "B": 1500.0, "C": 2500.0}
    },

    # ---------------------------------------------------------
    # 3. Suhu (2 Pertanyaan)
    # ---------------------------------------------------------
    {
        "id": "q_temp_1",
        "text": "Bagaimana rasanya sinar matahari saat siang hari di lahan?",
        "category": "temp",
        "options": [
            {"label": "Sejuk / Tidak terlalu panas", "value_code": "A", "description": "Dataran tinggi (< 20°C)"},
            {"label": "Hangat biasa", "value_code": "B", "description": "Sedang (20°C - 30°C)"},
            {"label": "Sangat menyengat / Terik", "value_code": "C", "description": "Dataran rendah panas (> 30°C)"}
        ],
        "values": {"A": 18.0, "B": 25.0, "C": 32.0}
    },
    {
        "id": "q_temp_2",
        "text": "Bagaimana suhu udara saat malam hari?",
        "category": "temp",
        "options": [
            {"label": "Dingin (perlu selimut tebal)", "value_code": "A", "description": "Suhu rendah"},
            {"label": "Sejuk nyaman", "value_code": "B", "description": "Suhu sedang"},
            {"label": "Gerah / Panas", "value_code": "C", "description": "Suhu tinggi"}
        ],
        "values": {"A": 18.0, "B": 25.0, "C": 32.0}
    },

    # ---------------------------------------------------------
    # 4. Sinar Matahari (2 Pertanyaan)
    # ---------------------------------------------------------
    {
        "id": "q_sun_1",
        "text": "Apakah lahan Anda tertutup bayangan pohon besar atau bangunan?",
        "category": "sun",
        "options": [
            {"label": "Ya, banyak naungan (teduh)", "value_code": "A", "description": "Intensitas rendah"},
            {"label": "Ada sedikit naungan", "value_code": "B", "description": "Intensitas sedang"},
            {"label": "Tidak ada, terbuka penuh", "value_code": "C", "description": "Intensitas tinggi"}
        ],
        "values": {"A": 0.3, "B": 0.6, "C": 1.0}
    },
    {
        "id": "q_sun_2",
        "text": "Berapa jam lahan mendapatkan sinar matahari langsung?",
        "category": "sun",
        "options": [
            {"label": "Kurang dari 4 jam", "value_code": "A", "description": "Rendah"},
            {"label": "4 - 7 jam", "value_code": "B", "description": "Sedang"},
            {"label": "Lebih dari 7 jam", "value_code": "C", "description": "Tinggi"}
        ],
        "values": {"A": 0.3, "B": 0.6, "C": 1.0}
    },

    # ---------------------------------------------------------
    # 5. Irigasi (2 Pertanyaan)
    # ---------------------------------------------------------
    {
        "id": "q_irr_1",
        "text": "Apakah tersedia sumber air (sungai/sumur) yang tidak pernah kering?",
        "category": "irrigation",
        "options": [
            {"label": "Tidak ada, hanya andalkan hujan", "value_code": "A", "description": "Rendah"},
            {"label": "Ada, tapi debit kecil/terbatas", "value_code": "B", "description": "Sedang"},
            {"label": "Ada, air melimpah sepanjang tahun", "value_code": "C", "description": "Tinggi"}
        ],
        "values": {"A": 0.3, "B": 0.6, "C": 1.0}
    },
    {
        "id": "q_irr_2",
        "text": "Seberapa mudah mengalirkan air ke lahan (ada saluran/pompa)?",
        "category": "irrigation",
        "options": [
            {"label": "Sulit, harus angkut manual", "value_code": "A", "description": "Sulit"},
            {"label": "Cukup mudah", "value_code": "B", "description": "Sedang"},
            {"label": "Sangat mudah (irigasi teknis)", "value_code": "C", "description": "Mudah"}
        ],
        "values": {"A": 0.3, "B": 0.6, "C": 1.0}
    },

    # ---------------------------------------------------------
    # 6. Tekstur Tanah (2 Pertanyaan)
    # ---------------------------------------------------------
    {
        "id": "q_soil_1",
        "text": "Ambil segenggam tanah basah lalu kepal. Apa yang terjadi?",
        "category": "soil",
        "options": [
            {"label": "Sangat lengket, bisa dibentuk panjang", "value_code": "A", "description": "Liat (Clay)"},
            {"label": "Bisa dibentuk bola tapi mudah retak", "value_code": "B", "description": "Lempung (Loam)"},
            {"label": "Ambyar, tidak bisa dibentuk", "value_code": "C", "description": "Pasir (Sandy)"}
        ],
        # Untuk soil, kita mapping ke string tipe tanah.
        # Karena ini kategorikal, kita mungkin perlu voting atau prioritas.
        # Kita gunakan skor numerik sementara untuk voting: Clay=1, Loam=2, Sandy=3
        "values": {"A": 1, "B": 2, "C": 3} 
    },
    {
        "id": "q_soil_2",
        "text": "Apa warna dominan tanah Anda saat basah?",
        "category": "soil",
        "options": [
            {"label": "Merah atau Kuning", "value_code": "A", "description": "Cenderung Liat/Clay"},
            {"label": "Hitam atau Coklat Gelap", "value_code": "B", "description": "Cenderung Lempung/Loam (Subur)"},
            {"label": "Abu-abu atau Putih", "value_code": "C", "description": "Cenderung Pasir/Sandy"}
        ],
        "values": {"A": 1, "B": 2, "C": 3}
    }
]

def get_questions() -> List[Question]:
    return [Question(**q) for q in QUESTIONS_DATA]

def map_answers_to_values(answers: List[Dict[str, str]]) -> Dict[str, any]:
    """
    Mengonversi jawaban user menjadi nilai teknis dengan merata-rata nilai 
    dari setiap pertanyaan dalam kategori yang sama.
    """
    # 1. Kelompokkan nilai berdasarkan kategori
    category_values = {
        "ph": [],
        "rain": [],
        "temp": [],
        "sun": [],
        "irrigation": [],
        "soil": []
    }
    
    # Lookup map untuk cepat mendapatkan value dari question_id + option_code
    q_map = {q['id']: q for q in QUESTIONS_DATA}
    
    for ans in answers:
        qid = ans.get('question_id')
        code = ans.get('selected_option')
        
        if qid in q_map:
            question_data = q_map[qid]
            category = question_data['category']
            
            # Ambil nilai numerik dari opsi yang dipilih
            if code in question_data['values']:
                val = question_data['values'][code]
                category_values[category].append(val)
                
    # 2. Hitung rata-rata
    result = {}
    
    # Mapping balik untuk Soil (numerik -> string)
    soil_reverse_map = {1: "Clay", 2: "Loam", 3: "Sandy"}
    
    for cat, vals in category_values.items():
        if not vals:
            # Default values jika user skip (safe defaults)
            if cat == "soil": result[cat] = "Loam"
            elif cat == "ph": result[cat] = 6.0
            elif cat == "rain": result[cat] = 1500.0
            elif cat == "temp": result[cat] = 25.0
            else: result[cat] = 0.6
            continue
            
        avg_val = statistics.mean(vals)
        
        if cat == "soil":
            # Untuk soil, kita bulatkan ke integer terdekat (1, 2, atau 3) lalu kembalikan ke string
            rounded_val = int(round(avg_val))
            result[cat] = soil_reverse_map.get(rounded_val, "Loam")
        else:
            # Untuk yang lain, gunakan nilai rata-rata float
            result[cat] = float(avg_val)
            
    return result
