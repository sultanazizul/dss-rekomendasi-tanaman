import numpy as np
from typing import List, Dict
# Mengimpor model data yang digunakan untuk menyimpan kriteria tanaman,
# hasil rekomendasi, dan detail kecocokan.
from app.models import Crop, Recommendation, MatchDetails

class AHPCalculator:
    """
    Kelas untuk menghitung bobot kriteria dan skor kecocokan tanaman
    menggunakan metode Analytical Hierarchy Process (AHP).
    """
    def __init__(self):
        # Kriteria yang digunakan: pH, Curah Hujan (Rain), Suhu (Temp), Sinar Matahari (Sun), Irigasi (Irrigation), Tanah (Soil)
        # Urutan ini harus sesuai dengan urutan baris/kolom dalam matriks perbandingan berpasangan.
        self.criteria = ["ph", "rain", "temp", "sun", "irrigation", "soil"]
        
        # Matriks Perbandingan Berpasangan (Pairwise Comparison Matrix) AHP.
        # Matriks ini menentukan kepentingan relatif antar kriteria (Skala Saaty 1-9).
        # Ini adalah contoh default yang disederhanakan dan seharusnya dapat disesuaikan.
        
        # Asumsi yang digunakan dalam matriks:
        # - Air (Hujan + Irigasi) sangat kritis (skala 5 terhadap Suhu/Matahari).
        # - Jenis Tanah dan pH kritis (skala 3 terhadap Suhu/Matahari).
        
        # Bentuk Matriks (6x6):
        #       pH   Rain Temp Sun  Irr  Soil
        # pH    1    1/3  3    3    1/3  1
        # Rain  3    1    5    5    1    3
        # Temp  1/3  1/5  1    1    1/5  1/3
        # Sun   1/3  1/5  1    1    1/5  1/3
        # Irr   3    1    5    5    1    3
        # Soil  1    1/3  3    3    1/3  1
        
        self.pairwise_matrix = np.array([
            [1.0, 1/3, 3.0, 3.0, 1/3, 1.0], # Baris pH
            [3.0, 1.0, 5.0, 5.0, 1.0, 3.0], # Baris Curah Hujan (Rain)
            [1/3, 1/5, 1.0, 1.0, 1/5, 1/3], # Baris Suhu (Temp)
            [1/3, 1/5, 1.0, 1.0, 1/5, 1/3], # Baris Sinar Matahari (Sun)
            [3.0, 1.0, 5.0, 5.0, 1.0, 3.0], # Baris Irigasi (Irrigation)
            [1.0, 1/3, 3.0, 3.0, 1/3, 1.0]  # Baris Tanah (Soil)
        ])
        
        # Menghitung Vektor Prioritas (Bobot) dari matriks perbandingan.
        self.weights = self._calculate_weights()
        # Menghitung Rasio Konsistensi (CR) untuk memverifikasi konsistensi penilaian.
        self.cr = self._calculate_consistency_ratio()

    def _calculate_weights(self) -> Dict[str, float]:
        """
        Menghitung Vektor Prioritas (bobot) kriteria menggunakan metode Eigenvector 
        (didekati dengan normalisasi kolom dan perataan baris).
        """
        # 1. Normalisasi matriks: bagi setiap elemen dengan jumlah kolomnya.
        column_sums = self.pairwise_matrix.sum(axis=0)
        normalized_matrix = self.pairwise_matrix / column_sums
        
        # 2. Hitung rata-rata setiap baris untuk mendapatkan bobot akhir (vektor prioritas).
        weights_array = normalized_matrix.mean(axis=1)
        
        # 3. Memetakan array bobot kembali ke nama kriteria.
        return dict(zip(self.criteria, weights_array))

    def _calculate_consistency_ratio(self) -> float:
        """
        Menghitung Rasio Konsistensi (CR) untuk memastikan matriks logis (CR <= 0.10 dianggap konsisten).
        """
        n = len(self.criteria)
        # Menghitung Lambda Max
        # 1. Kalikan matriks asli dengan vektor bobot.
        weights_vector = np.array(list(self.weights.values()))
        weighted_sum_vector = self.pairwise_matrix.dot(weights_vector)
        
        # 2. Bagi hasil perkalian dengan vektor bobot untuk mendapatkan vektor konsistensi.
        consistency_vector = weighted_sum_vector / weights_vector
        
        # 3. Lambda Max adalah rata-rata dari vektor konsistensi.
        lambda_max = consistency_vector.mean()
        
        # Indeks Konsistensi (CI)
        ci = (lambda_max - n) / (n - 1)
        
        # Indeks Acak (RI) untuk n=6 (didapat dari tabel AHP standar).
        ri = 1.24
        
        if ri == 0:
            return 0.0
            
        # Rasio Konsistensi (CR)
        cr = ci / ri
        return cr

    def calculate_match_score(self, user_val: float, min_val: float, max_val: float, is_categorical: bool = False, crop_val: str = None) -> float:
        """
        Menghitung seberapa baik kondisi pengguna (user_val) cocok dengan kebutuhan tanaman.
        Mengembalikan skor antara 0.0 (tidak cocok) dan 1.0 (cocok sempurna).
        """
        if is_categorical:
            # Kecocokan untuk nilai kategorikal (misalnya, Jenis Tanah).
            # Melakukan pencocokan sederhana.
            if str(user_val).lower() in str(crop_val).lower() or str(crop_val).lower() in str(user_val).lower():
                return 1.0 # Cocok sempurna
            return 0.0 # Tidak cocok
            
        # Kecocokan untuk rentang numerik
        
        # Jika berada di dalam rentang yang disyaratkan, skor 1.0
        if min_val <= user_val <= max_val:
            return 1.0
        
        # Hitung jarak ke batas rentang terdekat (min_val atau max_val)
        dist = min(abs(user_val - min_val), abs(user_val - max_val))
        
        # Tentukan ambang toleransi untuk penurunan skor.
        range_width = max_val - min_val
        if range_width == 0: range_width = 1 # Menghindari pembagian dengan nol
        
        # Heuristik: Mengizinkan penyimpangan hingga 50% dari lebar rentang (toleransi).
        tolerance = range_width * 0.5
        
        if dist > tolerance:
            # Jika di luar batas toleransi, skor 0.0
            return 0.0
            
        # Penurunan skor linier berdasarkan jarak terhadap toleransi.
        return 1.0 - (dist / tolerance)

    def rank_crops(self, user_inputs: Dict[str, any], crops: List[Crop]) -> List[Recommendation]:
        """
        Menghitung skor AHP untuk setiap tanaman berdasarkan input pengguna dan memberikan peringkat.
        """
        recommendations = []
        
        for crop in crops:
            # Hitung skor kecocokan (S_i) untuk setiap kriteria:
            
            # pH (Numerik)
            s_ph = self.calculate_match_score(user_inputs['ph'], crop.ph_min, crop.ph_max)
            
            # Curah Hujan (Numerik)
            s_rain = self.calculate_match_score(user_inputs['rain'], crop.rain_min, crop.rain_max)
            
            # Suhu (Numerik)
            s_temp = self.calculate_match_score(user_inputs['temp'], crop.temp_min, crop.temp_max)
            
            # Sinar Matahari (Dikonversi dari kategorikal ke rentang numerik 0-1 untuk perbandingan)
            sun_map = {'Low': 0.3, 'Medium': 0.6, 'High': 1.0}
            crop_sun_val = sun_map.get(crop.sun_requirement, 0.6)
            # Dibuat rentang kecil sekitar nilai konversi untuk skor kecocokan
            s_sun = self.calculate_match_score(user_inputs['sun'], crop_sun_val - 0.2, crop_sun_val + 0.2)
            
            # Irigasi (Dikonversi dari kategorikal ke rentang numerik 0-1)
            irr_map = {'Low': 0.3, 'Medium': 0.6, 'High': 1.0}
            crop_irr_val = irr_map.get(crop.irrigation_need, 0.6)
            s_irr = self.calculate_match_score(user_inputs['irrigation'], crop_irr_val - 0.2, crop_irr_val + 0.2)
            
            # Tanah (Kategorikal) - min_val/max_val diabaikan, is_categorical=True digunakan
            s_soil = self.calculate_match_score(user_inputs['soil'], 0, 0, is_categorical=True, crop_val=crop.soil_type)
            
            # Hitung Jumlah Tertimbang (Skor AHP Akhir)
            # Skor Akhir = Sum(Bobot_i * Skor_Kecocokan_i)
            
            final_score = (
                self.weights['ph'] * s_ph +
                self.weights['rain'] * s_rain +
                self.weights['temp'] * s_temp +
                self.weights['sun'] * s_sun +
                self.weights['irrigation'] * s_irr +
                self.weights['soil'] * s_soil
            )
            
            # Simpan rincian skor kecocokan
            match_details = MatchDetails(
                ph=s_ph,
                rain=s_rain,
                temp=s_temp,
                sun=s_sun,
                irrigation=s_irr,
                soil=s_soil
            )
            
            # Tambahkan hasil rekomendasi
            recommendations.append(Recommendation(
                crop_name=crop.name,
                score=round(final_score, 4),
                match_details=match_details
            ))
            
        # Urutkan rekomendasi berdasarkan skor dari yang tertinggi ke terendah
        recommendations.sort(key=lambda x: x.score, reverse=True)
        
        return recommendations