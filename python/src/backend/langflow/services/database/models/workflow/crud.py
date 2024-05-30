from uuid import UUID
from typing import Optional, Union
from datetime import datetime, timezone

from langflow.services.deps import get_session
from langflow.services.database.models.workflow.model import Workflow, WorkflowUpdate

from sqlmodel import Session, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.attributes import flag_modified

from fastapi import Depends, HTTPException, status

def get_workflow_by_id(db: Session, id: Union[UUID, str]) -> Union[Workflow, None]:
    return db.exec(select(Workflow).where(Workflow.id == id)).first()


def update_workflow(workflow_db: Optional[Workflow], workflow: WorkflowUpdate, db: Session = Depends(get_session)) -> Workflow:
    if not workflow_db:
        raise HTTPException(status_code=404, detail="Workflow not found")

    # user_db_by_username = get_user_by_username(db, user.username)  # type: ignore
    # if user_db_by_username and user_db_by_username.id != user_id:
    #     raise HTTPException(status_code=409, detail="Username already exists")

    workflow_data = workflow.model_dump(exclude_unset=True)
    changed = False
    for attr, value in workflow_data.items():
        if hasattr(workflow_db, attr) and value is not None:
            setattr(workflow_db, attr, value)
            changed = True

    if not changed:
        raise HTTPException(status_code=status.HTTP_304_NOT_MODIFIED, detail="Nothing to update")

    workflow_db.updated_at = datetime.now(timezone.utc)
    flag_modified(workflow_db, "updated_at")

    try:
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e)) from e

    return workflow_db