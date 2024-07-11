from uuid import UUID, uuid4
from datetime import datetime
from typing import List, Union
from pydantic import field_serializer, field_validator
from sqlmodel import Field, SQLModel, Column, Text
from sqlalchemy.dialects.mysql import LONGTEXT
from langflow.components.custom_components.schemas.workflow import TokenAndCost


class Workflow(SQLModel, table=True):
    id: str = Field(primary_key=True, unique=True, description="执行流ID")
    execute_id: UUID = Field(default_factory=uuid4, description="执行ID")
    create_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    execute_status: str = Field(default="RUNNING", description="工作流执行状态", include=["RUNNING", "FAILED", "SUCCESS"])
    reason: str = Field(default="")
    node_results: str = Field(default="[]", description="工作流中间节点结果，json格式列表，列表中的每一个原素是NodeData", sa_column=Column("node_results", LONGTEXT))
    token_and_cost: str = Field(default=TokenAndCost().model_dump_json(), description="工作流消耗tokens与计费", sa_column=Column("token_and_cost", Text))
    workflow_exe_cost: str = Field(default="0s", description="工作执行时间")

    # updated_at can be serialized to JSON
    @field_serializer("updated_at")
    def serialize_dt(self, dt: datetime, _info):
        if dt is None:
            return None
        return dt.isoformat()

    @field_validator("updated_at", mode="before")
    def validate_dt(cls, v):
        if v is None:
            return v
        elif isinstance(v, datetime):
            return v

        return datetime.fromisoformat(v)

class WorkflowCreate(SQLModel):
    id: str = Field(primary_key=True, unique=True, description="工作流ID, 同步Java端工作流ID")

class WorkflowRead(SQLModel):
    id: str = Field()
    create_at: datetime = Field()
    updated_at: datetime = Field()

class WorkflowUpdate(SQLModel):
    execute_status: str = Field(default="RUNNING", description="工作流执行状态", include=["RUNNING", "FAILED", "SUCCESS"])
    reason: str = Field(default="", description="")
    node_results: str = Field(default="[]", description="工作流中间节点结果，json格式列表，列表中的每一个原素是NodeData")
    token_and_cost: str = Field(default=TokenAndCost().model_dump_json(), description="工作流消耗tokens与计费")
    workflow_exe_cost: str = Field(default="0s", description="工作执行时间")

class WorkflowProgressRead(SQLModel):
    id: str = Field()
    execute_status: str = Field(default="RUNNING", description="工作流执行状态", include=["RUNNING", "FAILED", "SUCCESS"])
    reason: str = Field(default="")
    node_results: Union[List, str] = Field(description="工作流中间节点结果，json格式列表，列表中的每一个原素是NodeData")
    token_and_cost: Union[dict, str] = Field(default=TokenAndCost().model_dump_json(), description="工作流消耗tokens与计费")
    workflow_exe_cost: str = Field(description="工作执行时间")