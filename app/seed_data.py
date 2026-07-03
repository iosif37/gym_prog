import requests
import random
from datetime import datetime, timedelta

BASE_URL = "http://127.0.0.1:8000"

exercises = ["Bench Press", "Squat", "Deadlift", "Overhead Press", "Barbell Row"]

exercise_ids = {}
for name in exercises:
    resp = requests.post(f"{BASE_URL}/exercises", json={"name": name})
    if resp.status_code == 200:
        exercise_ids[name] = resp.json()["id"]
    elif resp.status_code == 400:
        all_ex = requests.get(f"{BASE_URL}/exercises").json()
        for ex in all_ex:
            if ex["name"] == name:
                exercise_ids[name] = ex["id"]

print("Exercise IDs:", exercise_ids)

starting_weights = {
    "Bench Press": 50,
    "Squat": 70,
    "Deadlift": 90,
    "Overhead Press": 30,
    "Barbell Row": 45,
}

today = datetime.utcnow()

for name, ex_id in exercise_ids.items():
    weight = starting_weights[name]
    for week in range(6):
        for session in range(2):  # 2 sessions per week
            # backdate: oldest session ~6 weeks ago, most recent ~today
            days_ago = (5 - week) * 7 + (1 - session) * 3
            session_time = today - timedelta(days=days_ago)

            weight += random.choice([0, 0, 2.5, 2.5, 5])
            for set_number in range(1, 4):  # 3 sets per session
                reps = random.choice([5, 6, 8, 8, 10])
                requests.post(
                    f"{BASE_URL}/sets",
                    json={
                        "exercise_id": ex_id,
                        "weight": weight,
                        "reps": reps,
                        "set_number": set_number,
                        "timestamp": session_time.isoformat(),
                    },
                )

print("Seed data created.")