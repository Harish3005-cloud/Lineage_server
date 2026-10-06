import os
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient
from sqlalchemy import text
from app.main import app
from app.db.database import SessionLocal, engine

client = TestClient(app)

def run_tests():
    print("=== Starting Phase 2 Verification Tests ===\n")
    
    # Clean up test users if any exist from previous runs
    db = SessionLocal()
    try:
        db.execute(text("DELETE FROM users WHERE email LIKE '%@test.com'"))
        db.commit()
    finally:
        db.close()

    # 1. Register Student (also testing under-18 user with age=17)
    print("Test 1: Register Student (Under-18: age=17)")
    student_payload = {
        "name": "Alice Student",
        "email": "alice.student@test.com",
        "password": "Password123!",
        "age": 17,
        "role": "STUDENT",
        "skills": ["python", "machine learning"],
        "availability": "part-time"
    }
    res = client.post("/api/auth/register", json=student_payload)
    assert res.status_code == 201, f"Failed: {res.text}"
    student_data = res.json()
    assert student_data["email"] == "alice.student@test.com"
    assert student_data["role"] == "STUDENT"
    assert student_data["age"] == 17
    assert student_data["is_under_18"] is True
    assert "password_hash" not in student_data
    assert "user_id" in student_data
    print("PASS: Student registered successfully with is_under_18 = True and no password_hash in response.\n")

    # 2. Register Expert
    print("Test 2: Register Expert")
    expert_payload = {
        "name": "Dr. Bob Expert",
        "email": "bob.expert@test.com",
        "password": "ExpertSecure456!",
        "age": 35,
        "role": "EXPERT",
        "skills": ["ai ethics", "system architecture"],
        "availability": "consultant"
    }
    res = client.post("/api/auth/register", json=expert_payload)
    assert res.status_code == 201, f"Failed: {res.text}"
    expert_data = res.json()
    assert expert_data["role"] == "EXPERT"
    assert expert_data["is_under_18"] is False
    assert "password_hash" not in expert_data
    print("PASS: Expert registered successfully.\n")

    # 3. Register Sponsor
    print("Test 3: Register Sponsor")
    sponsor_payload = {
        "name": "Charlie Sponsor",
        "email": "charlie.sponsor@test.com",
        "password": "SponsorPass789!",
        "age": 42,
        "role": "SPONSOR",
        "skills": ["venture funding", "mentorship"],
        "availability": "full-time"
    }
    res = client.post("/api/auth/register", json=sponsor_payload)
    assert res.status_code == 201, f"Failed: {res.text}"
    sponsor_data = res.json()
    assert sponsor_data["role"] == "SPONSOR"
    assert "password_hash" not in sponsor_data
    print("PASS: Sponsor registered successfully.\n")

    # 4. Attempt Admin registration and verify rejection
    print("Test 4: Attempt Admin registration (should be rejected)")
    admin_payload = {
        "name": "Eve Admin",
        "email": "eve.admin@test.com",
        "password": "AdminSecret999!",
        "age": 30,
        "role": "ADMIN",
        "skills": ["administration"],
        "availability": "full-time"
    }
    res = client.post("/api/auth/register", json=admin_payload)
    assert res.status_code in [400, 422], f"Expected 400 or 422, got {res.status_code}: {res.text}"
    print(f"PASS: Admin registration rejected as expected (HTTP {res.status_code}).\n")

    # 5. Login with valid credentials
    print("Test 5: Login with valid credentials")
    login_payload = {
        "email": "alice.student@test.com",
        "password": "Password123!"
    }
    res = client.post("/api/auth/login", json=login_payload)
    assert res.status_code == 200, f"Failed: {res.text}"
    token_data = res.json()
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"
    student_token = token_data["access_token"]
    print("PASS: Login succeeded and returned valid JWT token.\n")

    # 6. Login with incorrect password
    print("Test 6: Login with incorrect password")
    bad_login_payload = {
        "email": "alice.student@test.com",
        "password": "WrongPassword!"
    }
    res = client.post("/api/auth/login", json=bad_login_payload)
    assert res.status_code == 401, f"Expected 401, got {res.status_code}: {res.text}"
    print("PASS: Login with incorrect password rejected with HTTP 401.\n")

    # 7. Call /api/users/me with valid JWT
    print("Test 7: Call /api/users/me with valid JWT")
    res = client.get("/api/users/me", headers={"Authorization": f"Bearer {student_token}"})
    assert res.status_code == 200, f"Failed: {res.text}"
    me_data = res.json()
    assert me_data["email"] == "alice.student@test.com"
    assert me_data["user_id"] == student_data["user_id"]
    assert me_data["is_under_18"] is True
    assert "password_hash" not in me_data
    print("PASS: /api/users/me returned profile correctly with valid token.\n")

    # 8. Call /api/users/me without JWT
    print("Test 8: Call /api/users/me without JWT")
    res = client.get("/api/users/me")
    assert res.status_code == 401, f"Expected 401, got {res.status_code}: {res.text}"
    print("PASS: /api/users/me without JWT rejected with HTTP 401.\n")

    # 9. Verify duplicate email is rejected
    print("Test 9: Verify duplicate email is rejected")
    res = client.post("/api/auth/register", json=student_payload)
    assert res.status_code == 400, f"Expected 400, got {res.status_code}: {res.text}"
    print("PASS: Duplicate email registration rejected with HTTP 400.\n")

    # 10. Verify users table exists in lineage_db
    print("Test 10: Verify users table exists in lineage_db")
    from sqlalchemy import inspect
    insp = inspect(engine)
    tables = insp.get_table_names()
    assert "users" in tables, f"'users' table not found in tables: {tables}"
    cols = [c["name"] for c in insp.get_columns("users")]
    required_cols = ["user_id", "name", "email", "password_hash", "age", "role", "skills", "availability", "verification_status", "created_at"]
    for col in required_cols:
        assert col in cols, f"Missing required column: {col}"
    # 11. Verify Role-based authorization dependency
    print("Test 11: Verify require_role dependency")
    from app.api.deps import require_role
    from app.db.models.user import User, UserRole
    from fastapi import Depends

    # Attach a temporary test route to app to test role authorization
    @app.get("/api/test/expert-only")
    def expert_only_route(user: User = Depends(require_role(UserRole.EXPERT))):
        return {"access": "granted", "role": user.role}

    # Student trying to access expert route -> 403
    student_role_res = client.get("/api/test/expert-only", headers={"Authorization": f"Bearer {student_token}"})
    assert student_role_res.status_code == 403, f"Expected 403, got {student_role_res.status_code}"

    # Expert login and access -> 200
    expert_login = client.post("/api/auth/login", json={"email": "bob.expert@test.com", "password": "ExpertSecure456!"}).json()
    expert_token = expert_login["access_token"]
    expert_role_res = client.get("/api/test/expert-only", headers={"Authorization": f"Bearer {expert_token}"})
    assert expert_role_res.status_code == 200, f"Expected 200, got {expert_role_res.status_code}"
    print("PASS: Role-based authorization (require_role) correctly allowed expert and rejected student (403).\n")

    print("ALL 11 VERIFICATION TESTS COMPLETED SUCCESSFULLY!")

if __name__ == "__main__":
    run_tests()
