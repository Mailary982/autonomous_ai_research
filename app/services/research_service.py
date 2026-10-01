from uuid import UUID

from sqlalchemy.orm import Session

from app.models.research_run import ResearchRun
from app.models.research_task import ResearchTask
from app.repositories.research_repository import (
    create_run as repository_create_run,
    get_run as repository_get_run,
    get_tasks_for_run as repository_get_tasks_for_run,
)


def create_run(
    db: Session,
    objective: str,
    constraints: list[str],
    output_format: str,
) -> ResearchRun:
    """
    Create a research run.

    The API accepts constraints as a list.
    The current database schema stores them as text.
    """

    constraints_text = "\n".join(
        f"- {constraint}"
        for constraint in constraints
    )

    return repository_create_run(
        db=db,
        objective=objective,
        constraints=constraints_text,
        output_format=output_format,
    )


def get_run(
    db: Session,
    run_id: UUID,
) -> ResearchRun | None:
    """Retrieve a research run by ID."""

    return repository_get_run(
        db=db,
        run_id=run_id,
    )


def get_tasks(
    db: Session,
    run_id: UUID,
) -> list[ResearchTask]:
    """Retrieve all tasks belonging to a research run."""

    return repository_get_tasks_for_run(
        db=db,
        run_id=run_id,
    )