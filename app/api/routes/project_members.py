from datetime import datetime, timezone
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_project_member
from app.db.database import get_db
from app.db.models.user import User, UserRole
from app.db.models.project import Project
from app.db.models.project_member import ProjectMember, ProjectRole, MembershipStatus
from app.schemas.project_member import (
    ProjectCreate,
    ProjectResponse,
    ProjectMemberApply,
    ProjectMemberInvite,
    ProjectMemberResponse,
)

router = APIRouter(prefix="/projects", tags=["projects"])

def _map_user_role_to_project_role(user_role: UserRole) -> ProjectRole:
    if user_role == UserRole.EXPERT:
        return ProjectRole.EXPERT
    if user_role == UserRole.SPONSOR:
        return ProjectRole.SPONSOR
    return ProjectRole.STUDENT

@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(
    project_in: ProjectCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    project = Project(
        title=project_in.title,
        description=project_in.description,
        sponsor_id=current_user.user_id,
    )
    db.add(project)
    db.flush()

    # Automatically add sponsor as accepted member in ProjectMember
    sponsor_member = ProjectMember(
        project_id=project.project_id,
        user_id=current_user.user_id,
        role=ProjectRole.SPONSOR,
        status=MembershipStatus.ACCEPTED,
        joined_at=datetime.now(timezone.utc),
    )
    db.add(sponsor_member)
    db.commit()
    db.refresh(project)
    return project

@router.post("/{project_id}/apply", response_model=ProjectMemberResponse, status_code=status.HTTP_201_CREATED)
def apply_to_project(
    project_id: UUID,
    apply_in: Optional[ProjectMemberApply] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    project = db.query(Project).filter(Project.project_id == project_id).first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    existing = (
        db.query(ProjectMember)
        .filter(ProjectMember.project_id == project_id, ProjectMember.user_id == current_user.user_id)
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Membership record or application already exists for this project",
        )

    assigned_role = (
        apply_in.role if (apply_in and apply_in.role) else _map_user_role_to_project_role(current_user.role)
    )

    membership = ProjectMember(
        project_id=project_id,
        user_id=current_user.user_id,
        role=assigned_role,
        status=MembershipStatus.APPLIED,
    )
    db.add(membership)
    db.commit()
    db.refresh(membership)
    return membership

@router.post("/{project_id}/invite", response_model=ProjectMemberResponse, status_code=status.HTTP_201_CREATED)
def invite_to_project(
    project_id: UUID,
    invite_in: ProjectMemberInvite,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    project = db.query(Project).filter(Project.project_id == project_id).first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    if project.sponsor_id != current_user.user_id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the project sponsor can invite members",
        )

    target_user = db.query(User).filter(User.user_id == invite_in.user_id).first()
    if not target_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Target user not found")

    existing = (
        db.query(ProjectMember)
        .filter(ProjectMember.project_id == project_id, ProjectMember.user_id == invite_in.user_id)
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Membership record already exists for this user",
        )

    membership = ProjectMember(
        project_id=project_id,
        user_id=invite_in.user_id,
        role=invite_in.role or ProjectRole.STUDENT,
        status=MembershipStatus.INVITED,
    )
    db.add(membership)
    db.commit()
    db.refresh(membership)
    return membership

@router.put("/{project_id}/members/{user_id}/accept", response_model=ProjectMemberResponse)
def accept_member(
    project_id: UUID,
    user_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    project = db.query(Project).filter(Project.project_id == project_id).first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    if project.sponsor_id != current_user.user_id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the project sponsor can accept members",
        )

    member = (
        db.query(ProjectMember)
        .filter(ProjectMember.project_id == project_id, ProjectMember.user_id == user_id)
        .first()
    )
    if not member:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Membership record not found")

    if member.status not in (MembershipStatus.APPLIED, MembershipStatus.INVITED):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot accept member with status {member.status.value}",
        )

    member.status = MembershipStatus.ACCEPTED
    member.joined_at = datetime.now(timezone.utc)
    member.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(member)
    return member

@router.put("/{project_id}/members/{user_id}/reject", response_model=ProjectMemberResponse)
def reject_member(
    project_id: UUID,
    user_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    project = db.query(Project).filter(Project.project_id == project_id).first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    if project.sponsor_id != current_user.user_id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the project sponsor can reject applications",
        )

    member = (
        db.query(ProjectMember)
        .filter(ProjectMember.project_id == project_id, ProjectMember.user_id == user_id)
        .first()
    )
    if not member:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Membership record not found")

    if member.status != MembershipStatus.APPLIED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot reject member with status {member.status.value}",
        )

    member.status = MembershipStatus.REJECTED
    member.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(member)
    return member

@router.delete("/{project_id}/members/me", response_model=ProjectMemberResponse)
def leave_project(
    project_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    member = (
        db.query(ProjectMember)
        .filter(ProjectMember.project_id == project_id, ProjectMember.user_id == current_user.user_id)
        .first()
    )
    if not member or member.status != MembershipStatus.ACCEPTED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only active accepted members can leave the project",
        )

    member.status = MembershipStatus.LEFT
    member.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(member)
    return member

@router.get("/{project_id}/members", response_model=List[ProjectMemberResponse])
def get_project_members(
    project_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    project = db.query(Project).filter(Project.project_id == project_id).first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    caller_membership = (
        db.query(ProjectMember)
        .filter(ProjectMember.project_id == project_id, ProjectMember.user_id == current_user.user_id)
        .first()
    )
    is_sponsor = (project.sponsor_id == current_user.user_id) or (current_user.role == UserRole.ADMIN)

    if not is_sponsor and (not caller_membership or caller_membership.status != MembershipStatus.ACCEPTED):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not an accepted member of this project",
        )

    members = db.query(ProjectMember).filter(ProjectMember.project_id == project_id).all()
    return members

@router.get("/{project_id}/confidential-brief")
def get_confidential_project_brief(
    project_id: UUID,
    member: ProjectMember = Depends(require_project_member),
    db: Session = Depends(get_db),
):
    project = db.query(Project).filter(Project.project_id == project_id).first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return {
        "project_id": project.project_id,
        "title": project.title,
        "confidential_brief": project.description or "Confidential Brief Content",
        "member_role": member.role.value,
        "membership_status": member.status.value,
    }
