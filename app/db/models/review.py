import enum
import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, Text, DateTime, Enum as SAEnum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.database import Base

class ReviewStatus(str, enum.Enum):
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    CHANGES_REQUESTED = "CHANGES_REQUESTED"

class Review(Base):
    __tablename__ = "reviews"

    review_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    contribution_id = Column(UUID(as_uuid=True), ForeignKey("contributions.contribution_id", ondelete="CASCADE"), nullable=False)
    reviewer_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    status = Column(
        SAEnum(ReviewStatus, name="review_status_enum", values_callable=lambda obj: [e.value for e in obj]),
        nullable=False,
    )
    comments = Column(Text, nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    contribution = relationship("Contribution")
    reviewer = relationship("User")
