import os
import sys
from pathlib import Path
from uuid import uuid4

# Ensure project root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient
from sqlalchemy import text
from app.main import app
from app.db.database import SessionLocal, engine

client = TestClient(app)

def run_tests():
    print("=== Starting Project Membership Tests ===\n")
    
    # 0. Set up database clean state for test accounts & projects
    db = SessionLocal()
    try:
        db.execute(text("DELETE FROM project_members WHERE user_id IN (SELECT user_id FROM users WHERE email LIKE '%@pmtest.com')"))
        db.execute(text("DELETE FROM projects WHERE sponsor_id IN (SELECT user_id FROM users WHERE email LIKE '%@pmtest.com')"))
        db.execute(text("DELETE FROM users WHERE email LIKE '%@pmtest.com'"))
        db.commit()
    finally:
        db.close()

    # Create Sponsor user
    sponsor_reg = client.post("/api/auth/register", json={
        "name": "Sponsor Sam",
        "email": "sponsor@pmtest.com",
        "password": "Password123!",
        "age": 40,
        "role": "SPONSOR",
    })
    assert sponsor_reg.status_code == 201, f"Failed: {sponsor_reg.text}"
    sponsor_token = client.post("/api/auth/login", json={
        "email": "sponsor@pmtest.com",
        "password": "Password123!"
    }).json()["access_token"]
    sponsor_id = sponsor_reg.json()["user_id"]

    # Create Student Alice
    alice_reg = client.post("/api/auth/register", json={
        "name": "Student Alice",
        "email": "alice@pmtest.com",
        "password": "Password123!",
        "age": 20,
        "role": "STUDENT",
    })
    assert alice_reg.status_code == 201, f"Failed: {alice_reg.text}"
    alice_token = client.post("/api/auth/login", json={
        "email": "alice@pmtest.com",
        "password": "Password123!"
    }).json()["access_token"]
    alice_id = alice_reg.json()["user_id"]

    # Create Student Bob
    bob_reg = client.post("/api/auth/register", json={
        "name": "Student Bob",
        "email": "bob@pmtest.com",
        "password": "Password123!",
        "age": 21,
        "role": "STUDENT",
    })
    assert bob_reg.status_code == 201, f"Failed: {bob_reg.text}"
    bob_token = client.post("/api/auth/login", json={
        "email": "bob@pmtest.com",
        "password": "Password123!"
    }).json()["access_token"]
    bob_id = bob_reg.json()["user_id"]

    # Create Student Charlie (for rejection and other tests)
    charlie_reg = client.post("/api/auth/register", json={
        "name": "Student Charlie",
        "email": "charlie@pmtest.com",
        "password": "Password123!",
        "age": 19,
        "role": "STUDENT",
    })
    assert charlie_reg.status_code == 201, f"Failed: {charlie_reg.text}"
    charlie_token = client.post("/api/auth/login", json={
        "email": "charlie@pmtest.com",
        "password": "Password123!"
    }).json()["access_token"]
    charlie_id = charlie_reg.json()["user_id"]

    # Sponsor creates Project 1
    proj_resp = client.post("/api/projects", json={
        "title": "Quantum Robotics Initiative",
        "description": "Confidential research on robotics."
    }, headers={"Authorization": f"Bearer {sponsor_token}"})
    assert proj_resp.status_code == 201, f"Failed: {proj_resp.text}"
    project_id = proj_resp.json()["project_id"]

    # Sponsor creates Project 2 (for cross-project isolation test)
    proj2_resp = client.post("/api/projects", json={
        "title": "Second Project",
        "description": "Another project."
    }, headers={"Authorization": f"Bearer {sponsor_token}"})
    assert proj2_resp.status_code == 201, f"Failed: {proj2_resp.text}"
    project2_id = proj2_resp.json()["project_id"]

    print("Setup completed: Sponsor, Alice, Bob, Charlie and 2 Projects created.\n")

    # TEST 1: User applies to project
    print("Test 1: User applies to project")
    apply_resp = client.post(f"/api/projects/{project_id}/apply", headers={"Authorization": f"Bearer {alice_token}"})
    assert apply_resp.status_code == 201, f"Failed: {apply_resp.text}"
    apply_data = apply_resp.json()
    assert apply_data["status"] == "APPLIED"
    assert apply_data["user_id"] == alice_id
    assert apply_data["project_id"] == project_id
    print("PASS: Alice successfully applied with status = APPLIED.\n")

    # TEST 8: User with APPLIED -> 403 on protected resource
    print("Test 8: User with status APPLIED attempting to access confidential resource (should be 403)")
    brief_resp = client.get(f"/api/projects/{project_id}/confidential-brief", headers={"Authorization": f"Bearer {alice_token}"})
    assert brief_resp.status_code == 403, f"Expected 403, got {brief_resp.status_code}: {brief_resp.text}"
    assert "not an accepted member" in brief_resp.json()["detail"].lower()
    print("PASS: User with APPLIED status was denied access with 403.\n")

    # TEST 13: Non-sponsor attempting to accept a member -> 403
    print("Test 13: Non-sponsor attempting to accept member (should be 403)")
    non_sponsor_accept = client.put(
        f"/api/projects/{project_id}/members/{alice_id}/accept",
        headers={"Authorization": f"Bearer {bob_token}"}
    )
    assert non_sponsor_accept.status_code == 403, f"Expected 403, got {non_sponsor_accept.status_code}"
    print("PASS: Non-sponsor cannot accept members (403 Forbidden).\n")

    # TEST 2: Sponsor accepts user
    print("Test 2: Sponsor accepts user")
    accept_resp = client.put(
        f"/api/projects/{project_id}/members/{alice_id}/accept",
        headers={"Authorization": f"Bearer {sponsor_token}"}
    )
    assert accept_resp.status_code == 200, f"Failed: {accept_resp.text}"
    accept_data = accept_resp.json()
    assert accept_data["status"] == "ACCEPTED"
    assert accept_data["joined_at"] is not None
    print("PASS: Sponsor accepted Alice; status transitioned to ACCEPTED.\n")

    # TEST 3 & 5: Accepted user can access project confidential resource
    print("Test 3 & 5: Accepted user can access project & future confidential resources")
    alice_brief = client.get(f"/api/projects/{project_id}/confidential-brief", headers={"Authorization": f"Bearer {alice_token}"})
    assert alice_brief.status_code == 200, f"Expected 200, got {alice_brief.status_code}: {alice_brief.text}"
    assert alice_brief.json()["confidential_brief"] == "Confidential research on robotics."
    print("PASS: Accepted member successfully accessed confidential project brief.\n")

    # TEST 4: Accepted user can access project member list
    print("Test 4: Accepted user can access project member list")
    members_resp = client.get(f"/api/projects/{project_id}/members", headers={"Authorization": f"Bearer {alice_token}"})
    assert members_resp.status_code == 200, f"Failed: {members_resp.text}"
    members_data = members_resp.json()
    member_user_ids = [m["user_id"] for m in members_data]
    assert alice_id in member_user_ids
    assert sponsor_id in member_user_ids
    print(f"PASS: Member list retrieved ({len(members_data)} members).\n")

    # TEST 6: Unauthenticated user -> 401
    print("Test 6: Unauthenticated user (should be 401)")
    unauth_resp = client.get(f"/api/projects/{project_id}/confidential-brief")
    assert unauth_resp.status_code == 401, f"Expected 401, got {unauth_resp.status_code}"
    print("PASS: Unauthenticated request rejected with 401.\n")

    # TEST 7: User with no membership -> 403
    print("Test 7: User with no membership attempting access (should be 403)")
    no_member_resp = client.get(f"/api/projects/{project_id}/confidential-brief", headers={"Authorization": f"Bearer {bob_token}"})
    assert no_member_resp.status_code == 403, f"Expected 403, got {no_member_resp.status_code}"
    print("PASS: User with no membership denied access with 403.\n")

    # TEST 11: User attempting to access another project's resource -> 403
    print("Test 11: User attempting to access another project's resource (should be 403)")
    cross_project_resp = client.get(f"/api/projects/{project2_id}/confidential-brief", headers={"Authorization": f"Bearer {alice_token}"})
    assert cross_project_resp.status_code == 403, f"Expected 403, got {cross_project_resp.status_code}"
    print("PASS: Cross-project access denied with 403.\n")

    # TEST 12: Duplicate membership/application -> rejected
    print("Test 12: Duplicate application from Alice (should be rejected with 400)")
    dup_apply = client.post(f"/api/projects/{project_id}/apply", headers={"Authorization": f"Bearer {alice_token}"})
    assert dup_apply.status_code == 400, f"Expected 400, got {dup_apply.status_code}"
    print("PASS: Duplicate application rejected with 400.\n")

    # TEST 14: Non-sponsor attempting to reject a member -> 403
    print("Test 14: Non-sponsor attempting to reject member (should be 403)")
    # Charlie applies
    client.post(f"/api/projects/{project_id}/apply", headers={"Authorization": f"Bearer {charlie_token}"})
    non_sponsor_reject = client.put(
        f"/api/projects/{project_id}/members/{charlie_id}/reject",
        headers={"Authorization": f"Bearer {alice_token}"}
    )
    assert non_sponsor_reject.status_code == 403, f"Expected 403, got {non_sponsor_reject.status_code}"
    print("PASS: Non-sponsor cannot reject member (403 Forbidden).\n")

    # Sponsor rejects Charlie
    print("Sponsor rejects Charlie's application")
    sponsor_reject = client.put(
        f"/api/projects/{project_id}/members/{charlie_id}/reject",
        headers={"Authorization": f"Bearer {sponsor_token}"}
    )
    assert sponsor_reject.status_code == 200, f"Failed: {sponsor_reject.text}"
    assert sponsor_reject.json()["status"] == "REJECTED"
    print("PASS: Charlie's application status changed to REJECTED.\n")

    # TEST 9: User with REJECTED -> 403
    print("Test 9: User with REJECTED status attempting access (should be 403)")
    rejected_access = client.get(f"/api/projects/{project_id}/confidential-brief", headers={"Authorization": f"Bearer {charlie_token}"})
    assert rejected_access.status_code == 403, f"Expected 403, got {rejected_access.status_code}"
    print("PASS: Rejected user denied access with 403.\n")

    # TEST 10: User with LEFT -> 403
    print("Test 10: User leaves project (LEFT) and attempts access (should be 403)")
    leave_resp = client.delete(f"/api/projects/{project_id}/members/me", headers={"Authorization": f"Bearer {alice_token}"})
    assert leave_resp.status_code == 200, f"Failed: {leave_resp.text}"
    assert leave_resp.json()["status"] == "LEFT"
    
    # Alice attempts access after leaving -> 403
    left_access = client.get(f"/api/projects/{project_id}/confidential-brief", headers={"Authorization": f"Bearer {alice_token}"})
    assert left_access.status_code == 403, f"Expected 403, got {left_access.status_code}"
    print("PASS: User marked as LEFT denied access with 403; history preserved.\n")

    # Direct database query verification
    print("Database verification:")
    db = SessionLocal()
    try:
        rows = db.execute(text("SELECT project_member_id, project_id, user_id, role, status FROM project_members WHERE project_id = :pid"), {"pid": project_id}).fetchall()
        for r in rows:
            print(f"  Record: member={r[0]}, project={r[1]}, user={r[2]}, role={r[3]}, status={r[4]}")
        assert len(rows) >= 3, "Expected at least 3 membership records in DB"
    finally:
        db.close()

    print("\nALL 14 POSITIVE & NEGATIVE PROJECT MEMBERSHIP TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    run_tests()
