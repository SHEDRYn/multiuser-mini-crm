"""Main router for API v1"""

from fastapi import APIRouter

from app.api.v1 import analytics, auth, contacts, deals, organizations, tasks

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(organizations.router, prefix="/organizations", tags=["organizations"])
api_router.include_router(contacts.router, prefix="/contacts", tags=["contacts"])
api_router.include_router(deals.router, prefix="/deals", tags=["deals"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])

