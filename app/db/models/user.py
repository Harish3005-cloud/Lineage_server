import enum
import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, DateTime, Enum as SAEnum, JSON
from sqlalchemy.dialects.postgresql import UUID
from app.db.database import Base

class UserRole(str, enum.Enum):
    STUDENT = "STUDENT"
    EXPERT = "EXPERT"
    SPONSOR = "SPONSOR"
    ADMIN = "ADMIN"

class VerificationStatus(str, enum.Enum):
    PENDING = "PENDING"
    VERIFIED = "VERIFIED"
    REJECTED = "REJECTED"

class User(Base):
    __tablename__ = "users"

    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    age = Column(Integer, nullable=False)
    role = Column(
        SAEnum(UserRole, name="user_role_enum", values_callable=lambda obj: [e.value for e in obj]),
        nullable=False,
    )
    skills = Column(JSON, nullable=True, default=list)
    availability = Column(String(255), nullable=True)
    verification_status = Column(
        SAEnum(VerificationStatus, name="verification_status_enum", values_callable=lambda obj: [e.value for e in obj]),
        nullable=False,
        default=VerificationStatus.PENDING,
    )
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    @property
    def is_under_18(self) -> bool:
        return self.age < 18
