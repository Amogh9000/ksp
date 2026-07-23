import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from app.models.fir import FIRStatus, CrimeCategory


class FIRBase(BaseModel):
    fir_number: str
    year: int
    station_id: uuid.UUID
    crime_category: CrimeCategory
    sections_applied: Optional[str] = None
    status: FIRStatus = FIRStatus.REGISTERED
    incident_date: datetime
    incident_location: Optional[str] = None
    district: str
    complainant_name: Optional[str] = None
    complainant_phone: Optional[str] = None
    description: Optional[str] = None
    property_value: Optional[float] = None
    is_organized_crime: bool = False
    is_inter_district: bool = False


class FIRCreate(FIRBase):
    pass


class FIRUpdate(BaseModel):
    status: Optional[FIRStatus] = None
    investigating_officer_id: Optional[uuid.UUID] = None
    sections_applied: Optional[str] = None
    description: Optional[str] = None
    is_organized_crime: Optional[bool] = None


class FIRPublic(FIRBase):
    id: uuid.UUID
    investigating_officer_id: Optional[uuid.UUID] = None
    registered_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class FIRListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[FIRPublic]
