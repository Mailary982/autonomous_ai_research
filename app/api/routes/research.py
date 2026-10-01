from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.research import (
    ResearchRunCreate,
    ResearchRunDetailResponse,
    ResearchRunResponse,
    ResearchTaskResponse,
)
from app.services import research_service


router = APIRouter(
    prefix="/research",
    tags=["research"],
)


@router.post(
    "/runs",
    response_model=ResearchRunResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_research_run(
    payload: ResearchRunCreate,
    db: Session = Depends(get_db),
):
    """Create a new research run."""

    return research_service.create_run(
        db=db,
        objective=payload.objective,
        constraints=payload.constraints,
        output_format=payload.output_format,
    )


@router.get(
    "/runs/{run_id}",
    response_model=ResearchRunDetailResponse,
)
def get_research_run(
    run_id: UUID,
    db: Session = Depends(get_db),
):
    """Retrieve a research run together with its tasks."""

    run = research_service.get_run(
        db=db,
        run_id=run_id,
    )

    if run is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Research run not found.",
        )

    tasks = research_service.get_tasks(
        db=db,
        run_id=run_id,
    )

    return ResearchRunDetailResponse(
        id=run.id,
        user_id=run.user_id,
        objective=run.objective,
        constraints=run.constraints,
        output_format=run.output_format,
        status=run.status,
        config_version=run.config_version,
        error_message=run.error_message,
        cost=run.cost,
        created_at=run.created_at,
        updated_at=run.updated_at,
        tasks=tasks,
    )


@router.get(
    "/runs/{run_id}/tasks",
    response_model=list[ResearchTaskResponse],
)
def get_research_tasks(
    run_id: UUID,
    db: Session = Depends(get_db),
):
    """Retrieve tasks belonging to a research run."""

    run = research_service.get_run(
        db=db,
        run_id=run_id,
    )

    if run is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Research run not found.",
        )

    return research_service.get_tasks(
        db=db,
        run_id=run_id,
    )