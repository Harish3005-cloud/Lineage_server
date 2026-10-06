import enum
import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, Enum as SAEnum, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.database import Base

class ProjectRole(str, enum.Enum):
    STUDENT = "STUDENT"
    EXPERT = "EXPERT"
    SPONSOR = "SPONSOR"
    MENTOR = "MENTOR"

class MembershipStatus(str, enum.Enum):
    APPLIED = "APPLIED"
    INVITED = "INVITED"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    LEFT = "LEFT"

class ProjectMember(Base):
    __tablename__ = "project_members"

    project_member_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.project_id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    role = Column(
        SAEnum(ProjectRole, name="project_role_enum", values_callable=lambda obj: [e.value for e in obj]),
        nullable=False,
    )
    status = Column(
        SAEnum(MembershipStatus, name="membership_status_enum", values_callable=lambda obj: [e.value for e in obj]),
        nullable=False,
        default=MembershipStatus.APPLIED,
    )
    joined_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    __table_args__ = (
        UniqueConstraint("project_id", "user_id", name="uq_project_member_project_user"),
    )

    # Relationships
    project = relationship("Project", back_populates="members")
    user = relationship("User")
