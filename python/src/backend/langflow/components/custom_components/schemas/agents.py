from pydantic import BaseModel, Field
from typing import Literal, List, Union, Optional, Any, Dict

class ModelQuota(BaseModel):
    token_limit: int = Field(default=4096, description="token数上限")
    token_resp: int = Field(default=4000, description="响应token数大小")
    system_prompt_limit: int = Field(default=3276, description="系统提示词限制")

class ModelParameters(BaseModel):
    temperature: float = Field(default=0.5, ge=0.1, le=0.9, description="发散度")
    openai_api_key: str
    openai_base_url: str

class Model(BaseModel):
    """模型schema"""
    model_name: Literal["gpt-3.5-turbo", "qwen1.5-14b-chat"] = Field(description="模型名称")
    model_parameters: ModelParameters = Field(description="模型配置参数")
    model_quota: ModelQuota = Field(description="模型配额指标")


class Schema(BaseModel):
    type: Optional[str] = Field(description="当前schema的类型",
                                examples=["string", "integer", "number", "boolean", "list", "object"])
    name: Optional[str] = Field(default=None, description="当前schema的名称")
    schema: Optional[Union['Schema', List['Schema']]] = Field(default=None,
                                                              description="嵌套schema。例如当前type为object，object的schema也需要定义，需要嵌套定义schema",
                                                              examples=['[{"name": "param1"}, {"name": "param2"}]'])

    class Config:
        # This is required for self-referencing models
        orm_mode = True
        # allow_population_by_field_name = True

class InputSchema(BaseModel):
    name: str
    type: Optional[str]  # Literal["String", "Integer"]
    schema: Optional[Union[Schema, List[Schema]]] = Field(default=None,
                                                          description="当前类型schema。例如当前type为object，object的schema也需要定义，需要嵌套定义schema")

    class Config:
        orm_mode = True

class ToolSchema(BaseModel):
    """工具节点列表"""
    tool_id: str = Field(description="工具ID")
    tool_desc: str = Field(description="工具描述")
    tool_name: str
    input_schema: Optional[List[InputSchema]] = Field(default=None, description="工具节点输入数据结构")
    tenant_id: int = Field(description="租户ID")

class ToolNode(BaseModel):
    """工具节点schema"""
    tool_schemas: List[ToolSchema] = Field(description="工具节点的工具列表")


class KnowledgeSchema(BaseModel):
    """知识schema"""
    knowledge_id: str = Field(description="知识id")
    knowledge_name: str = Field(description="知识名称")
    knowledge_desc: str = Field(description="知识库工具描述")


class KnowledgeNode(BaseModel):
    knowledge_schemas: List[KnowledgeSchema] = Field(description="知识库节点的知识库列表")


class WorkflowSchema(BaseModel):
    """工作流schema"""
    workflow_id: str = Field(description="工作流id")
    workflow_name: str = Field(description="工作流名称")
    workflow_desc: str = Field(description="工作流描述")
    input_schema: Optional[List[InputSchema]] = Field(default=None, description="工作流输入")
    tenant_id: int = Field(description="租户ID")

class WorkflowNode(BaseModel):
    workflow_schemas: List[WorkflowSchema] = Field(description="工作流节点的工作流列表")

class Prompt(BaseModel):
    """提示schema"""
    prompt_content: str = Field(description="提示文本")

# class Memory(BaseModel):
#     """记忆schema"""
#     memory_key: str = Field(description="记忆id")
#     memory_input_key: str = Field(description="记忆输入key")
#     memory_output_key: str = Field(description="记忆输出key")

