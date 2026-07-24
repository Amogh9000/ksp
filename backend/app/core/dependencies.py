"""
FastAPI dependencies for authentication and role/jurisdiction-based access control.
"""
from uuid import UUID
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.core.security import decode_token
from app.models.officer import Officer, OfficerRole
from app.services.audit import log_action

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_officer(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> Officer:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_token(token)
        if payload.get("type") != "access":
            raise credentials_exception
        officer_id: str = payload.get("sub")
        if officer_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    result = await db.execute(
        select(Officer).where(Officer.id == UUID(officer_id))
    )
    officer = result.scalar_one_or_none()
    if officer is None or not officer.is_active:
        raise credentials_exception
    return officer


async def get_current_active_officer(
    current_officer: Officer = Depends(get_current_officer),
) -> Officer:
    if not current_officer.is_active:
        raise HTTPException(status_code=400, detail="Inactive officer account")
    return current_officer


# ---------------------------------------------------------------------------
# Role-based access factories
# ---------------------------------------------------------------------------

def require_role(*roles: OfficerRole):
    """Factory that returns a dependency enforcing one of the given roles."""
    async def _check(officer: Officer = Depends(get_current_active_officer)) -> Officer:
        if officer.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{officer.role}' does not have permission for this action.",
            )
        return officer
    return _check


def require_admin():
    return require_role(OfficerRole.ADMIN)


def require_analyst_or_above():
    return require_role(OfficerRole.ANALYST, OfficerRole.ADMIN)


def require_supervisor_or_above():
    return require_role(
        OfficerRole.SUPERVISOR, OfficerRole.ANALYST, OfficerRole.ADMIN
    )


# ---------------------------------------------------------------------------
# Jurisdiction check helper (call inside route handlers)
# ---------------------------------------------------------------------------

def assert_jurisdiction(officer: Officer, district: str):
    """
    Raise 403 if the officer doesn't have access to the requested district.
    ADMINs and ANALYSTs can see everything.
    SUPERVISORs can see their own district.
    OFFICERs can only see their station's district.
    """
    if officer.role in (OfficerRole.ADMIN, OfficerRole.ANALYST):
        return  # unrestricted
    officer_district = (
        officer.jurisdiction_district
        or (officer.station.district if officer.station else None)
    )
    if officer_district != district:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have jurisdiction over the requested district.",
        )
