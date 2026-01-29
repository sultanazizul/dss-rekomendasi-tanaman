# 👥 Pembagian Tugas Tim - Backend DSS Rekomendasi Tanaman

## 📋 Informasi Project

| Informasi | Detail |
|-----------|--------|
| **Nama Project** | Sistem Pendukung Keputusan Rekomendasi Tanaman |
| **Metode** | Analytical Hierarchy Process (AHP) |
| **Tech Stack** | Python, FastAPI, Supabase, Google Gemini AI |
| **Jumlah Anggota** | 4 Orang |

---

## 🧑‍💻 Anggota 1 - AHP Core Algorithm Developer

**Modul yang dikerjakan:** `app/ahp.py`

### Deskripsi Tugas
Mengembangkan inti algoritma AHP (Analytical Hierarchy Process) untuk menghitung bobot kriteria dan menentukan peringkat tanaman berdasarkan kesesuaian dengan kondisi lahan pengguna.

### Komponen yang Dikembangkan

| Komponen | Fungsi |
|----------|--------|
| `AHPCalculator.__init__()` | Inisialisasi matriks perbandingan berpasangan antar kriteria |
| `_calculate_weights()` | Menghitung bobot prioritas menggunakan metode Eigenvector |
| `_calculate_consistency_ratio()` | Menghitung Rasio Konsistensi (CR ≤ 0.10) |
| `calculate_match_score()` | Menghitung skor kecocokan kondisi user vs kebutuhan tanaman |
| `rank_crops()` | Memberi peringkat tanaman berdasarkan skor AHP |

### Kriteria AHP yang Diimplementasikan
- pH Tanah
- Curah Hujan (mm/tahun)
- Suhu (°C)
- Intensitas Matahari
- Ketersediaan Irigasi
- Jenis Tanah

---

## 🧑‍💻 Anggota 2 - Database & Data Models Developer

**Modul yang dikerjakan:** `app/database.py`, `app/models.py`, `schema.sql`

### Deskripsi Tugas
Merancang struktur database, koneksi ke Supabase, dan mendefinisikan model data yang digunakan di seluruh aplikasi.

### Komponen yang Dikembangkan

| File | Komponen | Fungsi |
|------|----------|--------|
| `database.py` | `get_supabase_client()` | Membuat koneksi ke Supabase |
| `schema.sql` | Tabel `crops` | Menyimpan data tanaman dan parameter pertumbuhan |
| `schema.sql` | Tabel `user_inputs` | Menyimpan input pengguna untuk analisis |
| `models.py` | `Crop` | Model data tanaman |
| `models.py` | `Question`, `QuestionOption` | Model pertanyaan kuesioner |
| `models.py` | `UserAnswer`, `UserInputSubmission` | Model input user |
| `models.py` | `Recommendation`, `MatchDetails` | Model hasil rekomendasi |

### Data Tanaman yang Di-seed
| Tanaman | pH | Curah Hujan | Suhu | Sinar Matahari | Jenis Tanah |
|---------|-----|-------------|------|----------------|-------------|
| Padi | 5.0-7.0 | 1500-2500 mm | 20-35°C | High | Clay |
| Jagung | 5.5-7.5 | 500-1500 mm | 18-32°C | High | Loam |
| Cabai | 5.5-6.8 | 600-1200 mm | 18-30°C | High | Sandy Loam |
| Tomat | 6.0-7.0 | 600-1500 mm | 18-27°C | High | Loam |
| Bawang Merah | 6.0-7.0 | 350-1000 mm | 25-32°C | High | Loam |
| Kentang | 5.0-6.5 | 1500-2500 mm | 15-20°C | Medium | Loam |
| Sawi | 6.0-7.0 | 1000-2000 mm | 20-30°C | Medium | Loam |

---

## 🧑‍💻 Anggota 3 - AI/Gemini Integration Developer

**Modul yang dikerjakan:** `app/ai.py`

### Deskripsi Tugas
Mengintegrasikan Google Gemini AI untuk fitur konsultasi interaktif dengan petani. AI dirancang untuk bertanya dengan bahasa yang mudah dipahami petani awam.

### Komponen yang Dikembangkan

| Komponen | Fungsi |
|----------|--------|
| `calculate_crop_recommendation()` | Function calling untuk kalkulasi rekomendasi via AI |
| `get_available_crops()` | Function calling untuk mendapatkan daftar tanaman |
| `get_chat_response()` | Handler utama untuk percakapan dengan AI |
| System Instruction | Prompt engineering untuk gaya bicara petani |

### Fitur AI yang Diimplementasikan
- **Model:** `gemini-2.5-flash`
- **Automatic Function Calling:** AI memanggil fungsi AHP saat sudah mengumpulkan data
- **Conversational Approach:** AI bertanya secara kualitatif, bukan teknis

### Contoh Pemetaan AI
| Pertanyaan AI | Jawaban User | Nilai Teknis |
|---------------|--------------|--------------|
| "Banyak cacing di tanah?" | "Lumayan banyak" | pH ≈ 7.0 |
| "Sering hujan?" | "Hampir tiap hari" | 2500 mm/tahun |
| "Udara di sana gimana?" | "Panas, dekat pantai" | 32°C |

---

## 🧑‍💻 Anggota 4 - API Routes & Mapping Developer

**Modul yang dikerjakan:** `app/main.py`, `app/mapping.py`

### Deskripsi Tugas
Membangun API endpoints menggunakan FastAPI dan sistem pemetaan jawaban kuesioner ke nilai teknis.

### API Endpoints yang Dikembangkan

| Method | Endpoint | Fungsi |
|--------|----------|--------|
| `GET` | `/api/questions` | Mendapatkan daftar pertanyaan kuesioner |
| `POST` | `/api/recommend` | Menghitung rekomendasi berdasarkan jawaban |
| `GET` | `/api/crops` | Mendapatkan daftar tanaman |
| `POST` | `/api/chat` | Endpoint untuk konsultasi AI |

### Sistem Mapping yang Dikembangkan

#### Kategori Pertanyaan (12 Pertanyaan Total)
| Kategori | Jumlah Pertanyaan | Contoh Pertanyaan |
|----------|-------------------|-------------------|
| pH Tanah | 3 | "Apakah tanah berbau masam?" |
| Curah Hujan | 2 | "Seberapa sering hujan di daerah Anda?" |
| Suhu | 2 | "Bagaimana suhu saat siang hari?" |
| Sinar Matahari | 2 | "Berapa jam lahan kena matahari?" |
| Irigasi | 2 | "Apakah ada sumber air terdekat?" |
| Jenis Tanah | 2 | "Jika tanah dikepal, apakah lengket?" |

### Fungsi Utama
| Fungsi | Deskripsi |
|--------|-----------|
| `get_questions()` | Mengembalikan semua pertanyaan dalam format Question model |
| `map_answers_to_values()` | Mengonversi jawaban A/B/C menjadi nilai teknis dengan rata-rata |

---

## 🔄 Alur Kerja Sistem (Flow)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        ALUR SISTEM BACKEND                              │
└─────────────────────────────────────────────────────────────────────────┘

                    ┌─────────────────────────────┐
                    │      USER REQUEST           │
                    └──────────────┬──────────────┘
                                   │
              ┌────────────────────┴────────────────────┐
              │                                         │
              ▼                                         ▼
    ┌─────────────────────┐                 ┌─────────────────────┐
    │   MODE KUESIONER    │                 │    MODE AI CHAT     │
    │   (Anggota 4)       │                 │    (Anggota 3)      │
    │   /api/questions    │                 │    /api/chat        │
    │   /api/recommend    │                 └──────────┬──────────┘
    └──────────┬──────────┘                            │
               │                                       │
               ▼                                       ▼
    ┌─────────────────────┐                 ┌─────────────────────┐
    │  MAPPING ANSWERS    │                 │   GEMINI AI         │
    │   (Anggota 4)       │                 │   (Anggota 3)       │
    │  mapping.py         │                 │   ai.py             │
    └──────────┬──────────┘                 └──────────┬──────────┘
               │                                       │
               └───────────────────┬───────────────────┘
                                   │
                                   ▼
                    ┌─────────────────────────────┐
                    │     AHP CALCULATION         │
                    │       (Anggota 1)           │
                    │       ahp.py                │
                    └──────────────┬──────────────┘
                                   │
                                   ▼
                    ┌─────────────────────────────┐
                    │       DATABASE              │
                    │       (Anggota 2)           │
                    │  database.py + models.py   │
                    └──────────────┬──────────────┘
                                   │
                                   ▼
                    ┌─────────────────────────────┐
                    │     RECOMMENDATION          │
                    │       RESPONSE              │
                    └─────────────────────────────┘
```

---

## 📁 Struktur File Backend

```
app/
├── ahp.py          # Anggota 1 - AHP Algorithm
├── database.py     # Anggota 2 - Database Connection
├── models.py       # Anggota 2 - Data Models
├── ai.py           # Anggota 3 - Gemini AI Integration
├── main.py         # Anggota 4 - API Endpoints
└── mapping.py      # Anggota 4 - Question Mapping

schema.sql          # Anggota 2 - Database Schema
requirements.txt    # Dependencies
.env                # Environment Variables
```

---

## ✅ Ringkasan Kontribusi

| Anggota | Modul | Lines of Code | Fokus Utama |
|---------|-------|---------------|-------------|
| **1** | `ahp.py` | ~191 | Algoritma AHP & Pemeringkatan |
| **2** | `database.py`, `models.py`, `schema.sql` | ~113 | Database & Data Models |
| **3** | `ai.py` | ~158 | Integrasi AI Gemini |
| **4** | `main.py`, `mapping.py` | ~372 | API Routes & Mapping |

---

*Dokumen ini dibuat untuk keperluan presentasi project kelompok.*
