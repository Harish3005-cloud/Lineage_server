import os
import sys
from pathlib import Path
from uuid import uuid4
from datetime import datetime, timezone
import pytest
from pydantic import ValidationError

# Ensure project root in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.schemas import (
    # Project
    ProjectStatus,
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse,
    # Charter
    CharterStatus,
    CharterCreate,
    CharterResponse,
    # Milestone
    MilestoneStatus,
    MilestoneCreate,
    MilestoneResponse,
    # Contribution
    ContributionStatus,
    ContributionCreate,
    ContributionResponse,
    # Escrow
    EscrowStatus,
    EscrowCreate,
    EscrowResponse,
    # Payout
    PayoutStatus,
    PayoutCreate,
    PayoutResponse,
    # Review
    IntegrityStatus,
    ReviewDecision,
    ReviewCreate,
    ReviewResponse,
    # Ledger
    LedgerActionType,
    LedgerEntryCreate,
    LedgerEntryResponse,
    # Dispute
    DisputeStatus,
    DisputeCreate,
    DisputeResponse,
    # Common
    PaginationParams,
    PaginationMeta,
)

def run_tests():
    print("=== Starting Schema Validation Tests ===\n")
    now = datetime.now(timezone.utc)
    proj_id = uuid4()
    user_id = uuid4()
    admin_id = uuid4()
    milestone_id = uuid4()
    contrib_id = uuid4()
    escrow_id = uuid4()

    # 1. Project Schema
    print("Test 1: Project schemas")
    proj_create = ProjectCreate(
        title="Project Apex",
        public_summary="Public project summary",
        confidential_brief="Confidential internal brief",
        status=ProjectStatus.ACTIVE,
        budget=50000.0,
    )
    assert proj_create.title == "Project Apex"
    assert proj_create.budget == 50000.0

    proj_resp = ProjectResponse(
        project_id=proj_id,
        sponsor_id=user_id,
        title="Project Apex",
        public_summary="Public summary",
        confidential_brief="Confidential brief",
        status=ProjectStatus.ACTIVE,
        budget=50000.0,
        created_at=now,
    )
    assert proj_resp.project_id == proj_id
    print("PASS: Project schemas instantiated successfully.\n")

    # 2. Charter Schema
    print("Test 2: Charter schemas")
    charter_create = CharterCreate(
        project_id=proj_id,
        version="1.0",
        scope="Build MVP for lineage tracking",
        roles={"lead": "student", "mentor": "expert"},
        reward_terms="Milestone based",
        acceptance_criteria="All tests passing",
        ip_terms="MIT Open Source",
        status=CharterStatus.ACTIVE,
    )
    assert charter_create.version == "1.0"
    charter_resp = CharterResponse(
        charter_id=uuid4(),
        project_id=proj_id,
        version=charter_create.version,
        scope=charter_create.scope,
        status=CharterStatus.ACTIVE,
        created_at=now,
    )
    assert charter_resp.status == CharterStatus.ACTIVE
    print("PASS: Charter schemas instantiated successfully.\n")

    # 3. Milestone Schema
    print("Test 3: Milestone schemas")
    ms_create = MilestoneCreate(
        project_id=proj_id,
        title="Milestone 1: Backend Architecture",
        description="Core schemas and auth",
        reward_amount=1000.0,
        status=MilestoneStatus.IN_PROGRESS,
    )
    assert ms_create.reward_amount == 1000.0
    ms_resp = MilestoneResponse(
        milestone_id=milestone_id,
        project_id=proj_id,
        title=ms_create.title,
        reward_amount=ms_create.reward_amount,
        status=MilestoneStatus.IN_PROGRESS,
        created_at=now,
    )
    assert ms_resp.milestone_id == milestone_id
    print("PASS: Milestone schemas instantiated successfully.\n")

    # 4. Contribution Schema
    print("Test 4: Contribution schemas")
    contrib_create = ContributionCreate(
        project_id=proj_id,
        milestone_id=milestone_id,
        user_id=user_id,
        human_owner_id=user_id,
        artifact_name="fastapi_core.py",
        artifact_hash="a1b2c3d4e5f67890",
        origin="HUMAN",
        ai_assisted=True,
        status=ContributionStatus.SUBMITTED,
    )
    assert contrib_create.ai_assisted is True
    contrib_resp = ContributionResponse(
        contribution_id=contrib_id,
        project_id=proj_id,
        milestone_id=milestone_id,
        user_id=user_id,
        human_owner_id=user_id,
        artifact_name=contrib_create.artifact_name,
        artifact_hash=contrib_create.artifact_hash,
        status=ContributionStatus.SUBMITTED,
        created_at=now,
    )
    assert contrib_resp.contribution_id == contrib_id
    print("PASS: Contribution schemas instantiated successfully.\n")

    # 5. Escrow Schema
    print("Test 5: Escrow schemas")
    escrow_create = EscrowCreate(
        project_id=proj_id,
        milestone_id=milestone_id,
        amount=1500.0,
        status=EscrowStatus.FUNDED,
        funded_at=now,
    )
    assert escrow_create.amount == 1500.0
    escrow_resp = EscrowResponse(
        escrow_id=escrow_id,
        project_id=proj_id,
        milestone_id=milestone_id,
        amount=1500.0,
        status=EscrowStatus.FUNDED,
        funded_at=now,
    )
    assert escrow_resp.escrow_id == escrow_id
    print("PASS: Escrow schemas instantiated successfully.\n")

    # 6. Payout Schema
    print("Test 6: Payout schemas")
    payout_create = PayoutCreate(
        escrow_id=escrow_id,
        user_id=user_id,
        contribution_id=contrib_id,
        amount=1500.0,
        reason="Milestone 1 completed successfully",
        status=PayoutStatus.PENDING,
    )
    assert payout_create.amount == 1500.0
    payout_resp = PayoutResponse(
        payout_id=uuid4(),
        escrow_id=escrow_id,
        user_id=user_id,
        contribution_id=contrib_id,
        amount=1500.0,
        reason=payout_create.reason,
        status=PayoutStatus.PENDING,
        created_at=now,
    )
    assert payout_resp.status == PayoutStatus.PENDING
    print("PASS: Payout schemas instantiated successfully.\n")

    # 7. Review Schema
    print("Test 7: Review schemas")
    review_create = ReviewCreate(
        contribution_id=contrib_id,
        reviewer_id=user_id,
        impact_score=92.5,
        similarity_score=0.15,
        integrity_status=IntegrityStatus.VERIFIED,
        decision=ReviewDecision.APPROVED,
        comments="Great modular design.",
    )
    assert review_create.impact_score == 92.5
    review_resp = ReviewResponse(
        review_id=uuid4(),
        contribution_id=contrib_id,
        reviewer_id=user_id,
        impact_score=92.5,
        similarity_score=0.15,
        integrity_status=IntegrityStatus.VERIFIED,
        decision=ReviewDecision.APPROVED,
        comments="Approved",
        created_at=now,
    )
    assert review_resp.integrity_status == IntegrityStatus.VERIFIED
    print("PASS: Review schemas instantiated successfully.\n")

    # 8. Ledger Entry Schema (admin_id only, NO actor_id)
    print("Test 8: Ledger Entry schemas (admin_id only)")
    ledger_create = LedgerEntryCreate(
        project_id=proj_id,
        contribution_id=contrib_id,
        admin_id=admin_id,
        action_type=LedgerActionType.CONTRIBUTION_RECORDED,
        payload={"action": "commit", "sha": "123abc"},
        previous_hash="0000000000000000",
        current_hash="1111111111111111",
    )
    assert ledger_create.admin_id == admin_id
    assert not hasattr(ledger_create, "actor_id")
    ledger_resp = LedgerEntryResponse(
        ledger_entry_id=uuid4(),
        project_id=proj_id,
        contribution_id=contrib_id,
        admin_id=admin_id,
        action_type=LedgerActionType.CONTRIBUTION_RECORDED,
        previous_hash="0000000000000000",
        current_hash="1111111111111111",
        created_at=now,
    )
    assert ledger_resp.admin_id == admin_id
    print("PASS: Ledger Entry schemas verified (admin_id only, no actor_id).\n")

    # 9. Dispute Schema
    print("Test 9: Dispute schemas")
    dispute_create = DisputeCreate(
        project_id=proj_id,
        raised_by=user_id,
        contribution_id=contrib_id,
        reason="Attribution discrepancy in artifact",
        status=DisputeStatus.OPEN,
    )
    assert dispute_create.status == DisputeStatus.OPEN
    dispute_resp = DisputeResponse(
        dispute_id=uuid4(),
        project_id=proj_id,
        raised_by=user_id,
        contribution_id=contrib_id,
        reason=dispute_create.reason,
        status=DisputeStatus.OPEN,
        created_at=now,
    )
    assert dispute_resp.dispute_id is not None
    print("PASS: Dispute schemas instantiated successfully.\n")

    # 10. Validation Negative Tests
    print("Test 10: Validation Negative Tests")
    
    # 10a. Invalid UUID
    try:
        CharterCreate(project_id="invalid-uuid-string", scope="Invalid")
        assert False, "Should have raised ValidationError for invalid UUID"
    except ValidationError:
        print("  [OK] Invalid UUID rejected")

    # 10b. Missing required fields
    try:
        MilestoneCreate(title="No project id")
        assert False, "Should have raised ValidationError for missing required fields"
    except ValidationError:
        print("  [OK] Missing required fields rejected")

    # 10c. Invalid enum values
    try:
        ReviewCreate(
            contribution_id=contrib_id,
            reviewer_id=user_id,
            decision="NON_EXISTENT_DECISION"
        )
        assert False, "Should have raised ValidationError for invalid enum value"
    except ValidationError:
        print("  [OK] Invalid enum value rejected")

    # 10d. Invalid review bounds (impact_score > 100 or similarity_score > 1.0)
    try:
        ReviewCreate(
            contribution_id=contrib_id,
            reviewer_id=user_id,
            impact_score=150.0  # max 100
        )
        assert False, "Should have raised ValidationError for impact_score > 100"
    except ValidationError:
        print("  [OK] Review impact_score > 100 rejected")

    try:
        ReviewCreate(
            contribution_id=contrib_id,
            reviewer_id=user_id,
            similarity_score=2.5  # max 1.0
        )
        assert False, "Should have raised ValidationError for similarity_score > 1.0"
    except ValidationError:
        print("  [OK] Review similarity_score > 1.0 rejected")

    # 10e. Invalid pagination parameters
    try:
        PaginationParams(page=0, page_size=20)
        assert False, "Should have raised ValidationError for page < 1"
    except ValidationError:
        print("  [OK] Pagination page < 1 rejected")

    try:
        PaginationParams(page=1, page_size=200)
        assert False, "Should have raised ValidationError for page_size > 100"
    except ValidationError:
        print("  [OK] Pagination page_size > 100 rejected")

    print("\nALL SCHEMA VALIDATION AND NEGATIVE TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    run_tests()
