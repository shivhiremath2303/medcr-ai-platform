from typing import List, Dict
from fastapi import APIRouter, Depends, HTTPException, Query
from app.core.security.dependencies import get_current_active_user, CurrentUser, rate_limit
from app.di import get_background_task_provider
from app.domain.repositories.background_tasks import BackgroundTaskProvider
from app.domain.models.background_task import BackgroundTask

router = APIRouter(
    prefix="/tasks",
    tags=["Tasks"],
    dependencies=[Depends(rate_limit)],
)

@router.get("/status", response_model=Dict[str, BackgroundTask])
async def get_batch_task_status(
    task_ids: List[str] = Query(..., description="List of task IDs to check"),
    task_provider: BackgroundTaskProvider = Depends(get_background_task_provider),
    current_user: CurrentUser = Depends(get_current_active_user),
):
    """
    Retrieve status for multiple background tasks in a single request (Batching 10.3.7).
    """
    results = {}
    for tid in task_ids:
        task = await task_provider.get_task(tid)
        if task:
            results[tid] = task
    return results

@router.get("/{task_id}", response_model=BackgroundTask)
async def get_task_status(
    task_id: str,
    task_provider: BackgroundTaskProvider = Depends(get_background_task_provider),
    current_user: CurrentUser = Depends(get_current_active_user),
):
    """Get status for a single background task."""
    task = await task_provider.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task
