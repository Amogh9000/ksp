import uuid
from datetime import datetime
from sqlalchemy import (
    String, DateTime, Text, ForeignKey, Enum as SAEnum,
    func, Boolean, Numeric
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.base import Base
import enum


class FIRStatus(str, enum.Enum):
    REGISTERED = "registered"
    UNDER_INVESTIGATION = "under_investigation"
    CHARGESHEETED = "chargesheeted"
    CLOSED = "closed"
    TRANSFERRED = "transferred"
    FINAL_REPORT = "final_report"


class CrimeCategory(str, enum.Enum):
    MURDER = "murder"
    ATTEMPT_TO_MURDER = "attempt_to_murder"
    KIDNAPPING = "kidnapping"
    ROBBERY = "robbery"
    DACOITY = "dacoity"
    THEFT = "theft"
    BURGLARY = "burglary"
    CHEATING = "cheating"
    FRAUD = "fraud"
    CYBER_CRIME = "cyber_crime"
    DRUG_OFFENCE = "drug_offence"
    ASSAULT = "assault"
    SEXUAL_ASSAULT = "sexual_assault"
    DOMESTIC_VIOLENCE = "domestic_violence"
    MOTOR_VEHICLE_THEFT = "motor_vehicle_theft"
    EXTORTION = "extortion"
    ARSON = "arson"
    FORGERY = "forgery"
    OTHER = "other"


class FIR(Base):
    __tablename__ = "firs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    # e.g. "CR No. 42/2024"
    fir_number: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    year: Mapped[int] = mapped_column(nullable=False)

    station_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("stations.id"), nullable=False
    )
    investigating_officer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("officers.id"), nullable=True
    )

    crime_category: Mapped[CrimeCategory] = mapped_column(
        SAEnum(CrimeCategory, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
    )
    # IPC/BNS section(s) invoked — stored as comma-separated text
    sections_applied: Mapped[str] = mapped_column(String(500), nullable=True)

    status: Mapped[FIRStatus] = mapped_column(
        SAEnum(FIRStatus, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=FIRStatus.REGISTERED,
    )

    incident_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    incident_location: Mapped[str] = mapped_column(String(500), nullable=True)
    district: Mapped[str] = mapped_column(String(100), nullable=False)

    complainant_name: Mapped[str] = mapped_column(String(200), nullable=True)
    complainant_phone: Mapped[str] = mapped_column(String(20), nullable=True)

    description: Mapped[str] = mapped_column(Text, nullable=True)

    # Property / vehicle stolen amount
    property_value: Mapped[float] = mapped_column(Numeric(14, 2), nullable=True)

    is_organized_crime: Mapped[bool] = mapped_column(Boolean, default=False)
    is_inter_district: Mapped[bool] = mapped_column(Boolean, default=False)

    registered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    station: Mapped["Station"] = relationship("Station", back_populates="firs")
    investigating_officer: Mapped["Officer"] = relationship(
        "Officer", back_populates="firs_filed"
    )
    accused: Mapped[list["CriminalLink"]] = relationship(
        "CriminalLink", back_populates="fir", lazy="selectin"
    )
