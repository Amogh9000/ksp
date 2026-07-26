import uuid
from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel


class CriminalBase(BaseModel):
    ksp_criminal_id: str
    full_name: str
    alias: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    nationality: str = "Indian"
    district: Optional[str] = None
    state: str = "Karnataka"
    present_address: Optional[str] = None
    is_wanted: bool = False


class CriminalCreate(CriminalBase):
    aadhaar_number: Optional[str] = None


class CriminalPublic(CriminalBase):
    id: uuid.UUID
    total_cases: int
    is_repeat_offender: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class CriminalListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[CriminalPublic]
