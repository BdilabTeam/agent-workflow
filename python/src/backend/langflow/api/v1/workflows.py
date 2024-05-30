import json
from uuid import UUID, uuid4
from typing import Union

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session


from langflow.services.database.models.workflow.model import Workflow, WorkflowCreate, WorkflowUpdate, WorkflowRead, WorkflowProgressRead
from langflow.services.database.models.workflow.crud import get_workflow_by_id, update_workflow
from langflow.services.deps import get_session

router = APIRouter(tags=["Workflow"], prefix="/workflow")


@router.post("/", response_model=WorkflowRead, status_code=201)
def add_workflow(
    workflow: WorkflowCreate,
    session: Session = Depends(get_session),
) -> Workflow:
    """
    Add a new workflow to the database.
    """
    new_workflow = Workflow.model_validate(workflow, from_attributes=True)
    try:
        session.add(new_workflow)
        session.commit()
        session.refresh(new_workflow)
    except IntegrityError as e:
        session.rollback()
        raise HTTPException(status_code=500, detail="This workflow is unavailable.") from e

    return new_workflow

@router.patch("/{workflow_id}", response_model=WorkflowRead)
def patch_workflow(
    workflow_id: Union[UUID, str],
    workflow_update: WorkflowUpdate,
    session: Session = Depends(get_session),
) -> Workflow:
    """
    Update an existing workflow data.
    """

    if workflow_db := get_workflow_by_id(session, workflow_id):
        return update_workflow(workflow_db, workflow_update, session)
    else:
        raise HTTPException(status_code=500, detail="User not found")

@router.get("/get_progress/{workflow_id}", response_model=WorkflowProgressRead)
def get_workflow_progress(
    workflow_id: Union[UUID, str],
    session: Session = Depends(get_session),
) -> Workflow:
    """
    Retrieve the current workflow progress data.
    """
    if not (workflow_db := get_workflow_by_id(db=session, id=workflow_id)):
        raise HTTPException(status_code=500, detail="Workflow not found")

    workflow_data = workflow_db.model_dump()
    workflow_progress_data = WorkflowProgressRead(**workflow_data)
    workflow_progress_data.node_results = json.loads(workflow_db.node_results)
    workflow_progress_data.token_and_cost = json.loads(workflow_db.token_and_cost)
    return workflow_progress_data

@router.delete("/{workflow_id}", response_model=dict)
def delete_workflow(
    workflow_id: Union[UUID, str],
    session: Session = Depends(get_session),
) -> dict:
    """
    Delete a workflow from the database.
    """
    if not (workflow_db := get_workflow_by_id(db=session, id=workflow_id)):
        raise HTTPException(status_code=500, detail="Workflow not found")

    session.delete(workflow_db)
    session.commit()

    return {"detail": "Workflow deleted"}