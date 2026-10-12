"""Task service"""

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ForbiddenException, NotFoundException, ValidationException
from app.models.activity import ActivityType
from app.models.organization_member import OrganizationMember
from app.models.task import Task
from app.repositories.activity import ActivityRepository
from app.repositories.deal import DealRepository
from app.repositories.task import TaskRepository
from app.schemas.task import TaskCreate, TaskListParams, TaskUpdate
from app.services.permissions import PermissionService


class TaskService:
    """Task service"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.task_repo = TaskRepository(db)
        self.deal_repo = DealRepository(db)
        self.activity_repo = ActivityRepository(db)

    async def get_tasks(
        self, params: TaskListParams, organization_id: int, membership: OrganizationMember
    ) -> list[Task]:
        """Get tasks with filters"""
        if params.deal_id:
            # Verify deal exists and user has access
            deal = await self.deal_repo.get(params.deal_id)
            if not deal or deal.organization_id != organization_id:
                raise NotFoundException("Deal not found")

            return await self.task_repo.get_by_deal(
                deal_id=params.deal_id,
                only_open=params.only_open,
                due_before=params.due_before,
                due_after=params.due_after,
            )
        else:
            return await self.task_repo.get_organization_tasks(
                organization_id=organization_id,
                only_open=params.only_open,
                due_before=params.due_before,
                due_after=params.due_after,
            )

    async def get_task(
        self, task_id: int, organization_id: int, membership: OrganizationMember
    ) -> Task:
        """Get single task"""
        task = await self.task_repo.get(task_id)
        if not task:
            raise NotFoundException("Task not found")

        # Verify task belongs to organization
        deal = await self.deal_repo.get(task.deal_id)
        if not deal or deal.organization_id != organization_id:
            raise NotFoundException("Task not found")

        return task

    async def create_task(
        self, data: TaskCreate, organization_id: int, membership: OrganizationMember
    ) -> Task:
        """Create new task"""
        # Verify deal exists and belongs to organization
        deal = await self.deal_repo.get(data.deal_id)
        if not deal or deal.organization_id != organization_id:
            raise ValidationException("Invalid deal")

        # Business rule: members can only create tasks for their own deals
        if PermissionService.is_member_role(membership):
            if deal.owner_id != membership.user_id:
                raise ForbiddenException("You can only create tasks for your own deals")

        task = await self.task_repo.create(
            {
                "deal_id": data.deal_id,
                "title": data.title,
                "description": data.description,
                "due_date": data.due_date,
            }
        )

        # Create activity
        await self.activity_repo.create(
            {
                "deal_id": data.deal_id,
                "author_id": membership.user_id,
                "type": ActivityType.TASK_CREATED,
                "payload": {"task_id": task.id, "task_title": task.title},
            }
        )

        await self.db.commit()
        return task

    async def update_task(
        self,
        task_id: int,
        data: TaskUpdate,
        organization_id: int,
        membership: OrganizationMember,
    ) -> Task:
        """Update task"""
        task = await self.get_task(task_id, organization_id, membership)
        deal = await self.deal_repo.get(task.deal_id)

        # Check permissions
        if not PermissionService.can_manage_all_resources(membership):
            if deal.owner_id != membership.user_id:
                raise ForbiddenException("You can only modify tasks for your own deals")

        update_data = data.model_dump(exclude_unset=True)
        task = await self.task_repo.update(task, update_data)
        await self.db.commit()
        return task

    async def delete_task(
        self, task_id: int, organization_id: int, membership: OrganizationMember
    ) -> None:
        """Delete task"""
        task = await self.get_task(task_id, organization_id, membership)
        deal = await self.deal_repo.get(task.deal_id)

        # Check permissions
        if not PermissionService.can_manage_all_resources(membership):
            if deal.owner_id != membership.user_id:
                raise ForbiddenException("You can only delete tasks for your own deals")

        await self.task_repo.delete(task_id)
        await self.db.commit()

