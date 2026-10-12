"""Task endpoints"""

from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_membership, get_organization_id
from app.db.session import get_db
from app.models.organization_member import OrganizationMember
from app.schemas.task import TaskCreate, TaskListParams, TaskResponse, TaskUpdate
from app.services.task import TaskService

router = APIRouter()


@router.get("", response_model=list[TaskResponse])
async def get_tasks(
    organization_id: Annotated[int, Depends(get_organization_id)],
    membership: Annotated[OrganizationMember, Depends(get_current_membership)],
    db: Annotated[AsyncSession, Depends(get_db)],
    deal_id: int | None = None,
    only_open: bool = False,
    due_before: date | None = None,
    due_after: date | None = None,
) -> list[TaskResponse]:
    """
    Get list of tasks with optional filters.

    Filters:
    - deal_id: Filter by specific deal
    - only_open: Show only uncompleted tasks
    - due_before: Tasks due before this date
    - due_after: Tasks due after this date
    """
    params = TaskListParams(
        deal_id=deal_id,
        only_open=only_open,
        due_before=due_before,
        due_after=due_after,
    )
    task_service = TaskService(db)
    return await task_service.get_tasks(params, organization_id, membership)


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: int,
    organization_id: Annotated[int, Depends(get_organization_id)],
    membership: Annotated[OrganizationMember, Depends(get_current_membership)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TaskResponse:
    """Get single task by ID"""
    task_service = TaskService(db)
    return await task_service.get_task(task_id, organization_id, membership)


@router.post("", response_model=TaskResponse, status_code=201)
async def create_task(
    data: TaskCreate,
    organization_id: Annotated[int, Depends(get_organization_id)],
    membership: Annotated[OrganizationMember, Depends(get_current_membership)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TaskResponse:
    """
    Create a new task.

    Business rules:
    - due_date cannot be in the past
    - Members can only create tasks for their own deals
    """
    task_service = TaskService(db)
    return await task_service.create_task(data, organization_id, membership)


@router.patch("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    data: TaskUpdate,
    organization_id: Annotated[int, Depends(get_organization_id)],
    membership: Annotated[OrganizationMember, Depends(get_current_membership)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TaskResponse:
    """Update a task (members can only update tasks for their own deals)"""
    task_service = TaskService(db)
    return await task_service.update_task(task_id, data, organization_id, membership)


@router.delete("/{task_id}", status_code=204)
async def delete_task(
    task_id: int,
    organization_id: Annotated[int, Depends(get_organization_id)],
    membership: Annotated[OrganizationMember, Depends(get_current_membership)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    """Delete a task"""
    task_service = TaskService(db)
    await task_service.delete_task(task_id, organization_id, membership)

