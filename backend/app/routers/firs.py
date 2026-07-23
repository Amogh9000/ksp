from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.database import get_db
from app.models.fir import FIR
from app.models.officer import Officer
from app.schemas.fir import FIRCreate, FIRUpdate, FIRPublic, FIRListResponse
from app.core.dependencies import (
    get_current_active_officer,
    require_supervisor_or_above,
    assert_jurisdiction,
)
from app.services.audit import log_action

router = APIRouter(prefix="/firs", tags=["FIRs"])


@router.get("", response_model=FIRListResponse)
async def list_firs(
    request: Request,
    district: str | None = Query(None),
    status: str | None = Query(None),
    category: str | None = Query(None),
    year: int | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    current_officer: Officer = Depends(get_current_active_officer),
):
    query = select(FIR)

    # Jurisdiction filter: officers only see their district unless analyst/admin
    from app.models.officer import OfficerRole
    if current_officer.role == OfficerRole.OFFICER:
        officer_district = (
            current_officer.jurisdiction_district
            or (current_officer.station.district if current_officer.station else None)
        )
        if officer_district:
            query = query.where(FIR.district == officer_district)
    elif current_officer.role == OfficerRole.SUPERVISOR:
        officer_district = (
            current_officer.jurisdiction_district
            or (current_officer.station.district if current_officer.station else None)
        )
        if district and district != officer_district:
            raise HTTPException(status_code=403, detail="Outside your jurisdiction.")
        if officer_district:
            query = query.where(FIR.district == officer_district)

    if district:
        query = query.where(FIR.district == district)
    if status:
        query = query.where(FIR.status == status)
    if category:
        query = query.where(FIR.crime_category == category)
    if year:
        query = query.where(FIR.year == year)

    count_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total = count_result.scalar_one()

    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    firs = result.scalars().all()

    await log_action(
        db,
        action="LIST_FIRS",
        officer_id=current_officer.id,
        resource_type="fir",
        request=request,
        request_summary={"district": district, "page": page},
        response_status=200,
    )

    return FIRListResponse(total=total, page=page, page_size=page_size, items=firs)


@router.get("/{fir_id}", response_model=FIRPublic)
async def get_fir(
    fir_id: UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_officer: Officer = Depends(get_current_active_officer),
):
    result = await db.execute(select(FIR).where(FIR.id == fir_id))
    fir = result.scalar_one_or_none()
    if not fir:
        raise HTTPException(status_code=404, detail="FIR not found.")

    assert_jurisdiction(current_officer, fir.district)

    await log_action(
        db,
        action="READ_FIR",
        officer_id=current_officer.id,
        resource_type="fir",
        resource_id=str(fir_id),
        request=request,
        response_status=200,
    )
    return fir


@router.post("", response_model=FIRPublic, status_code=status.HTTP_201_CREATED)
async def create_fir(
    body: FIRCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_officer: Officer = Depends(require_supervisor_or_above()),
):
    fir = FIR(**body.model_dump())
    db.add(fir)
    await db.flush()

    await log_action(
        db,
        action="CREATE_FIR",
        officer_id=current_officer.id,
        resource_type="fir",
        resource_id=str(fir.id),
        request=request,
        response_status=201,
    )
    return fir


@router.patch("/{fir_id}", response_model=FIRPublic)
async def update_fir(
    fir_id: UUID,
    body: FIRUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_officer: Officer = Depends(require_supervisor_or_above()),
):
    result = await db.execute(select(FIR).where(FIR.id == fir_id))
    fir = result.scalar_one_or_none()
    if not fir:
        raise HTTPException(status_code=404, detail="FIR not found.")

    assert_jurisdiction(current_officer, fir.district)

    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(fir, field, value)

    await log_action(
        db,
        action="UPDATE_FIR",
        officer_id=current_officer.id,
        resource_type="fir",
        resource_id=str(fir_id),
        request=request,
        request_summary=body.model_dump(exclude_unset=True),
        response_status=200,
    )
    return fir
