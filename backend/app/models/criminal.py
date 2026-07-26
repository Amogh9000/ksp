import uuid
from datetime import date, datetime
from sqlalchemy import String, DateTime, Date, Text, Integer, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.base import Base


class Criminal(Base):
    __tablename__ = "criminals"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    # Government-issued IDs (nullable — not always available at arrest)
    aadhaar_number: Mapped[str] = mapped_column(String(12), unique=True, nullable=True)
    # Internal KSP identifier
    ksp_criminal_id: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)

    full_name: Mapped[str] = mapped_column(String(200), nullable=False)
    alias: Mapped[str] = mapped_column(String(500), nullable=True)   # comma-separated aliases
    date_of_birth: Mapped[date] = mapped_column(Date, nullable=True)
    gender: Mapped[str] = mapped_column(String(20), nullable=True)
    nationality: Mapped[str] = mapped_column(String(100), default="Indian")
    religion: Mapped[str] = mapped_column(String(100), nullable=True)

    # Address
    present_address: Mapped[str] = mapped_column(Text, nullable=True)
    permanent_address: Mapped[str] = mapped_column(Text, nullable=True)
    district: Mapped[str] = mapped_column(String(100), nullable=True)
    state: Mapped[str] = mapped_column(String(100), default="Karnataka")

    # Physical descriptors
    height_cm: Mapped[int] = mapped_column(Integer, nullable=True)
    identifying_marks: Mapped[str] = mapped_column(Text, nullable=True)
    photo_url: Mapped[str] = mapped_column(String(500), nullable=True)

    # Offence history summary
    total_cases: Mapped[int] = mapped_column(Integer, default=0)
    is_repeat_offender: Mapped[bool] = mapped_column(default=False)
    is_wanted: Mapped[bool] = mapped_column(default=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    fir_appearances: Mapped[list["CriminalLink"]] = relationship(
        "CriminalLink", back_populates="criminal", lazy="selectin"
    )
