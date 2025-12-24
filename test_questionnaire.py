
import requests
import json
import statistics

# 1. Test fetching questions
print("--- Fetching Questions ---")
try:
    response = requests.get("http://127.0.0.1:8000/api/questions")
    if response.status_code == 200:
        questions = response.json()
        print(f"Success! Got {len(questions)} questions.")
        for q in questions[:3]: # Show first 3
             print(f"- {q['id']}: {q['text']}")
    else:
        print(f"Failed to fetch questions: {response.status_code}")
except Exception as e:
    print(f"Connection failed: {e}")

# 2. Test submitting answers (Simulated)
print("\n--- Submitting Answers ---")
# Simulating a user who has fertile land (High pH, ample rain, etc.)
payload = {
    "answers": [
        # pH: 2 questions A (7.0), 1 question B (6.0) -> Avg ~ 6.66
        {"question_id": "q_ph_1", "selected_option": "A"}, 
        {"question_id": "q_ph_2", "selected_option": "A"}, # A is 5.0 in updated mapping? Let's check
        # Checking mapping.py source in my head... 
        # q_ph_1 A=7.0
        # q_ph_2 A=5.0 (Masam) -> Oh wait, I want fertile. 
        # q_ph_2 B=6.5, C=7.0. Let's pick C for q_ph_2
        {"question_id": "q_ph_2", "selected_option": "C"},
        {"question_id": "q_ph_3", "selected_option": "C"}, # C=7.0
        
        # Rain: High
        {"question_id": "q_rain_1", "selected_option": "C"}, # 2500
        {"question_id": "q_rain_2", "selected_option": "C"}, # 2500
        
        # Temp: Medium
        {"question_id": "q_temp_1", "selected_option": "B"}, # 25
        {"question_id": "q_temp_2", "selected_option": "B"}, # 25
        
        # Sun: High
        {"question_id": "q_sun_1", "selected_option": "C"}, # 1.0
        {"question_id": "q_sun_2", "selected_option": "C"}, # 1.0
        
        # Irr: High
        {"question_id": "q_irr_1", "selected_option": "C"}, # 1.0
        {"question_id": "q_irr_2", "selected_option": "C"}, # 1.0
        
        # Soil: Loam (B)
        {"question_id": "q_soil_1", "selected_option": "B"}, # 2
        {"question_id": "q_soil_2", "selected_option": "B"}  # 2
    ]
}

try:
    response = requests.post("http://127.0.0.1:8000/api/recommend", json=payload)
    if response.status_code == 200:
        data = response.json()
        print("Success! Recommendations received.")
        print("Top 3 Crops:")
        for rec in data['recommendations'][:3]:
            print(f"1. {rec['crop_name']} (Score: {rec['score']})")
    else:
        print(f"Failed to get recommendations: {response.status_code}")
        print(response.text)
except Exception as e:
    print(f"Connection failed: {e}")
