from uuid import UUID

from sqlalchemy.orm import Session

from app.models.research_run import ResearchRun, ResearchRunStatus
from app.models.research_task import ResearchTask


def create_run(
    db: Session,
    objective: str,
    constraints: str,
    output_format: str,
) -> ResearchRun:
    """Create and persist a new research run."""

    run = ResearchRun(
        objective=objective,
        constraints=constraints,
        output_format=output_format,
        status=ResearchRunStatus.PENDING,
        config_version="v1",
    )

    db.add(run)
    db.commit()
    db.refresh(run)

    return run


def get_run(
    db: Session,
    run_id: UUID,
) -> ResearchRun | None:
    """Retrieve a research run by ID."""

    return (
        db.query(ResearchRun)
        .filter(ResearchRun.id == run_id)
        .first()
    )


def create_task(
    db: Session,
    run_id: UUID,
    task_type: str,
    description: str,
    dependencies: str | None = None,
    parent_id: UUID | None = None,
    max_retries: int = 2,
) -> ResearchTask:
    """Create and persist a research task."""

    task = ResearchTask(
        run_id=run_id,
        parent_id=parent_id,
        task_type=task_type,
        description=description,
        dependencies=dependencies,
        status="PENDING",
        retry_count=0,
        max_retries=max_retries,
    )

    db.add(task)
    db.commit()
    db.refresh(task)

    return task


def get_tasks_for_run(
    db: Session,
    run_id: UUID,
) -> list[ResearchTask]:
    """Retrieve all tasks belonging to a research run."""

    return (
        db.query(ResearchTask)
        .filter(ResearchTask.run_id == run_id)
        .order_by(ResearchTask.created_at.asc())
        .all()
    )