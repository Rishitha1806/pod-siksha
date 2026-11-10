import os
import sys
import dotenv

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
dotenv.load_dotenv(".env")
assert os.getenv("DATABASE_URL"), "DATABASE_URL is required"

from fastapi.testclient import TestClient
import server

client = TestClient(server.app)

headers = {"Authorization": "Bearer session_demo_learner_001"}
teacher_headers = {"Authorization": "Bearer session_demo_teacher_001"}

print("--- 1. Testing /api/health ---")
res = client.get("/api/health")
print("Status:", res.status_code, "Health data:", res.json())
assert res.status_code == 200
assert res.json()["database"] == "connected"

print("\n--- 2. Testing /api/auth/me (Learner profile) ---")
res = client.get("/api/auth/me", headers=headers)
print("Status:", res.status_code, "User:", res.json())
assert res.status_code == 200
assert res.json()["user"]["email"] == "learner@demo.in"

print("\n--- 3. Testing /api/user/journeys (Personal Journeys from Neon) ---")
res = client.get("/api/user/journeys", headers=headers)
print("Status:", res.status_code)
assert res.status_code == 200
journeys = res.json()
print(f"Retrieved {len(journeys)} learning journeys for learner from Neon PostgreSQL!")

print("\n--- 4. Testing /api/insights/personal (Personal Telemetry & Mastery) ---")
res = client.get("/api/insights/personal", headers=headers)
print("Status:", res.status_code)
assert res.status_code == 200
insights = res.json()
print(f"Personal Insights: Mastery = {insights.get('cognitive_mastery')}%")

print("\n--- 5. Testing /api/misconceptions (Radar) ---")
res = client.get("/api/misconceptions", headers=headers)
print("Status:", res.status_code, "Count:", len(res.json()))
assert res.status_code == 200

print("\n--- 6. Testing /api/memory-loop ---")
res = client.get("/api/memory-loop", headers=headers)
print("Status:", res.status_code, "Count:", len(res.json()))
assert res.status_code == 200

print("\n--- 7. Testing /api/dashboard (Teacher Observatory) ---")
res = client.get("/api/dashboard", headers=teacher_headers)
print("Status:", res.status_code)
assert res.status_code == 200

print("\n--- 8. Testing Concept DNA with First Session ---")
j_items = journeys.get("journeys", journeys) if isinstance(journeys, dict) else journeys
if j_items and len(j_items) > 0:
    sess_id = j_items[0]["id"]
    res = client.get(f"/api/concept-dna/{sess_id}", headers=headers)
    print(f"Status for session {sess_id}:", res.status_code)
    assert res.status_code == 200
    print("Concept DNA nodes:", len(res.json().get("nodes", [])))

print("\n--- 9. Testing Teacher Observatory Recommendations ---")
teacher_headers = {"Authorization": "Bearer session_demo_teacher_001"}
res = client.get("/api/teacher/recommendations", headers=teacher_headers)
print("Teacher recommendations status:", res.status_code)
assert res.status_code == 200

print("\n--- 10. Testing Teacher CSV Export ---")
res = client.get("/api/teacher/export/csv", headers=teacher_headers)
print("Teacher CSV status:", res.status_code, "Content length:", len(res.content))
assert res.status_code == 200

print("\n==========================================")
print(" ALL 10 NEON DATABASE SUITE TESTS PASSED!")
print("==========================================")
