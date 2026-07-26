"""
Audit logging service.
All API routes should call log_action() before returning.
The function is fire-and-forget: it never raises so a logging failure
never breaks a user-facing response.
"""
from __future__ import annotations

import logging
from typing import Any
from uuid import UUID

from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_log import AuditLog

logger = logging.getLogger(__name__)


async def log_action(
    db: AsyncSession,
    *,
    action: str,
    officer_id: UUID | None = None,
    actor_label: str | None = None,
    resource_type: str | None = None,
    resource_id: str | None = None,
    request: Request | None = None,
    request_summary: dict[str, Any] | None = None,
    response_status: int | None = None,
) -> None:
    """
    Persist one audit record. Swallows all exceptions so callers are safe.
    """
    try:
        ip = None
        method = None
        endpoint = None
        if request is not None:
            ip = request.client.host if request.client else None
            method = request.method
            endpoint = str(request.url.path)

        entry = AuditLog(
            officer_id=officer_id,
            actor_label=actor_label,
            action=action,
            resource_type=resource_type,
            resource_id=str(resource_id) if resource_id else None,
            http_method=method,
            endpoint=endpoint,
            ip_address=ip,
            request_summary=request_summary,
            response_status=response_status,
        )
        db.add(entry)
        # We do NOT commit here — the route handler or middleware commits the session.
    except Exception as exc:  # noqa: BLE001
        logger.warning("Audit log failed: %s", exc)
