import os
import sys
import uuid
import dotenv

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
dotenv.load_dotenv(".env")
assert os.getenv("DATABASE_URL"), "DATABASE_URL is required"

from fastapi.testclient import TestClient
import server

client = TestClient(server.app)

test_email = f"neon_test_{uuid.uuid4().hex[:6]}@demo.in"
test_password = "SecurePassword123!"
test_name = "Neon Verification Learner"

print("--- Testing Registration with Neon ---")
res = client.post("/api/auth/register", json={
    "email": test_email,
    "password": test_password,
    "full_name": test_name,
    "preferred_language": "te"
})
print("Register status:", res.status_code, res.json())
assert res.status_code == 200
user_data = res.json().get("user", {})

print("\n--- Testing Login with Neon ---")
res = client.post("/api/auth/login", json={
    "email": test_email,
    "password": test_password
})
print("Login status:", res.status_code)
assert res.status_code == 200
login_data = res.json()
token = login_data["token"]
print("Received Auth Token from Neon session storage!")

auth_headers = {"Authorization": f"Bearer {token}"}

print("\n--- Testing Authenticated /api/auth/me ---")
res = client.get("/api/auth/me", headers=auth_headers)
print("Auth me status:", res.status_code, res.json())
assert res.status_code == 200
assert res.json()["user"]["email"] == test_email

print("\n--- Testing Data Isolation (New user has 0 journeys) ---")
res = client.get("/api/user/journeys", headers=auth_headers)
print("Journeys status:", res.status_code)
assert res.status_code == 200
journeys = res.json().get("journeys", [])
print(f"Isolated journeys for new user: {len(journeys)} (Expect 0)")
assert len(journeys) == 0

print("\n--- Testing Logout & Session Invalidation ---")
res = client.post("/api/auth/logout", headers=auth_headers)
print("Logout status:", res.status_code)
assert res.status_code == 200

print("\n--- Verifying Revoked Session Cannot Access Protected Routes ---")
res = client.get("/api/auth/me", headers=auth_headers)
print("Post-logout access status:", res.status_code)
assert res.status_code == 401
print("Access correctly rejected with 401 Unauthorized!")

print("\n=======================================================")
print(" AUTHENTICATION, REGISTRATION & ISOLATION PASSED NEON!")
print("=======================================================")
