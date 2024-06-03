from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Literal, List, Union, Optional, Any


class RefContent(BaseModel):
    source_id: str = Field(description="源节点ID")
    name: str = Field(description="引用字段路径", examples=["ouput1", "output1.param1"])

class Value(BaseModel):
    type: Literal["ref", "literal"] = Field(description="当前值类型，ref表示引用前置节点输出；literal表示用户输入")
    # java转-使用Any、python转-str
    content: Union[str, RefContent] = Field(description="当前值内容", examples=["用户输入", '{"source": "block-output", "blockID": "100001", "name": "p10.p101"}'])

class Schema(BaseModel):
    type: Optional[str] = Field(description="当前schema的类型", examples=["string", "integer", "number", "boolean", "list", "object"])
    name: Optional[str] = Field(default=None, description="当前schema的名称")
    schema: Optional[Union['Schema', List['Schema']]] = Field(default=None, description="嵌套schema。例如当前type为object，object的schema也需要定义，需要嵌套定义schema", examples=['[{"name": "param1"}, {"name": "param2"}]'])
    # required: bool = False

    class Config:
        # This is required for self-referencing models
        orm_mode = True
        # allow_population_by_field_name = True
        
class Input(BaseModel):
    type: Optional[str]   # Literal["String", "Integer"]
    schema: Optional[Union[Schema, List[Schema]]] = Field(default=None, description="当前类型schema。例如当前type为object，object的schema也需要定义，需要嵌套定义schema", examples=['[{"name": "param1"}, {"name": "param2"}]'])
    value: Value
    
    class Config:
        orm_mode = True

class InputParameter(BaseModel):
    name: str
    input: Input

class Inputs(BaseModel):
    """输入schema"""
    inputParameters: List[InputParameter]

class Output(BaseModel):
    type: str = Field(description="字段类型", examples=["string", "integer", "number", "boolean"])
    name: str = Field(description="字段名称")
    schema: Optional[Union[Schema, List[Schema]]] = Field(default=None, description="当前类型schema。例如当前type为object，object的schema也需要定义，需要嵌套定义schema", examples=['[{"name": "param1"}, {"name": "param2"}]'])
    # required: bool = False

    class Config:
        orm_mode = True
        allow_population_by_field_name = True

class Outputs(BaseModel):
    """输出schema"""
    outputs: List[Output]

class ModelQuota(BaseModel):
    token_limit: Optional[int] = Field(default=4096, description="token数上限")
    token_resp: Optional[int] = Field(default=4000, description="响应token数大小")
    system_prompt_limit: Optional[int] = Field(default=3276, description="系统提示词限制")

class ModelParameters(BaseModel):
    temperature: Optional[float] = Field(default=0.5, ge=0.1, le=0.9, description="发散度")
    openai_api_key: Optional[str] = Field(default="EMPTY")
    openai_base_url: Optional[str] = Field(default="http://172.18.22.19:7002/v1")

class Model(BaseModel):
    """模型schema"""
    model_name: Literal["qwen1.5-14b-chat", "gpt-3.5-turbo-0125", "gpt-3.5-turbo-1106", "gpt-4-turbo-preview", "gpt-4-0125-preview", "gpt-4-1106-preview", "gpt-4-vision-preview"] = Field(description="模型名称")
    model_parameters: Optional[ModelParameters] = Field(description="模型配置参数")
    model_quota: Optional[ModelQuota] = Field(description="模型配额指标")
    
class ModelList(BaseModel):
    model_list: List[Model]

class NodeBase(BaseModel):
    flow_id: str = Field(description="流ID，用于关联中间结果")
    node_id: str = Field(description="节点ID")
    input_schema: Inputs = Field(description="结束节点输入数据结构")
    
    @field_validator("flow_id", mode="before")
    def validate_dt(cls, v):
        if not v:
            raise ValueError("工作流ID不能为空")
        
        return v
    
    @field_validator("node_id", mode="before")
    def validate_dt(cls, v):
        if not v:
            raise ValueError("节点ID不能为空")
        
        return v

class StartNode(NodeBase):
    """开始节点schema"""
    flow_id: str = Field(description="流ID，用于关联中间结果")
    node_id: str = Field(description="节点ID")
    input_schema: Inputs = Field(description="结束节点输入数据结构")
    # output_schema: Outputs = Field(description="结束节点输出数据结构")

class EndNode(NodeBase):
    """结束节点schema"""
    flow_id: str = Field(description="流ID，用于关联中间结果")
    node_id: str = Field(description="节点ID")
    prompt: str = Field(description="输出格式化")
    input_schema: Inputs = Field(description="结束节点输入数据结构")
    # output_schema: Outputs = Field(description="结束节点输出数据结构")

class LLMNode(NodeBase):
    """LLM节点schema"""
    flow_id: str = Field(description="流ID，用于关联中间结果")
    node_id: str = Field(description="节点ID")
    input_schema: Inputs = Field(description="LLM节点输入数据结构")
    output_schema: Outputs = Field(description="LLM节点输出数据结构")
    prompt: str = Field(description="大模型提示词")
    model_schema: Model = Field(description="大模型配置信息")
    
class ToolNode(NodeBase):
    """工具节点schema"""
    tenant_id: Union[int, str] = Field(description="租户ID")
    flow_id: str = Field(description="流ID，用于关联中间结果")
    node_id: str = Field(description="节点ID")
    tool_ids: List[str] = Field(description="工具ID列表", examples=["1", "2"])
    input_schema: Inputs = Field(description="工具节点输入数据结构")
    # output_schema: Outputs = Field(description="LLM节点输出数据结构")
    
class KnowledgeConfig(BaseModel):
    search_strategy: Literal["semantic", "hybrid", "fulltext"] = Field(default="semantic", description="搜索策略")
    maximum_number_of_recalls: int = Field(default=3, ge=1, le=9, description="最大召回数")
    minimum_matching_degree: float = Field(default=0.75, ge=0.01, le=0.99, description="最小相似度")

class Knowledge(BaseModel):
    knowledge_name: str = Field(description="知识名称")
    knowledge_config: KnowledgeConfig

class KnowledgeNode(NodeBase):
    """知识节点schema"""
    tenant_id: Union[int, str] = Field(description="租户ID")
    flow_id: str = Field(description="流ID，用于关联中间结果")
    node_id: str = Field(description="节点ID")
    knowledge_ids: List[str] = Field(description="知识库ID列表", examples=["1", "2"])
    input_schema: Inputs = Field(description="知识节点输入数据结构")
    knowledge_schema: Knowledge = Field(description="知识检索配置信息")

class TokenAndCost(BaseModel):
    input_tokens: str = Field(default="0 Tokens", description="输入tokens")
    input_cost: str = Field(default="$0.0", description="输入tokens计费金额")
    output_tokens: str = Field(default="0 Tokens",description="输出tokens")
    output_cost: str = Field(default="$0.0", description="输初tokens计费金额")
    total_tokens: str = Field(default="0 Tokens",description="总tokens")
    total_cost: str = Field(default="$0.0", description="总计tokens计费金额")

class NodeData(BaseModel):
    node_id: str = Field(default="", description="节点ID")
    node_type: str = Field(description="节点类型")
    node_name: str = Field(default="", description="节点名称")
    node_status: Literal["RUNNING", "FAILED", "SUCCESS"] = Field(default="RUNNING", description="节点状态")
    error_info: Optional[str] = Field(default="", description="节点状态为：FAILED时，需提供错误信息")
    input: str = Field(default="", description="节点解析后的输入")
    output: str = Field(default="", description="节点解析后的输出")
    node_exe_cost: str = Field(default="0s", description="节点运行时间")
    raw_output: str = Field(default="", description="节点原始输出")
    extra: Optional[str] = Field(default="", description="额外信息")
    token_and_cost: TokenAndCost = Field(default=TokenAndCost(), description="tokens与计费")

class NodeResponse(BaseModel):
    node_data: NodeData = Field(description="当前节点输出数据")

class StartNodeResponse(NodeResponse):
    """开始节点响应Schema"""

class LLMNodeResponse(NodeResponse):
    """LLM节点响应Schema"""

class ToolNodeResponse(NodeResponse):
    """工具节点响应Schema"""

class KnowledgeNodeResponse(NodeResponse):
    """知识节点响应Schema"""

class EndNodeResponse(NodeResponse):
    """结束节点响应Schema"""
    all_nodes_data: List[NodeData] = Field(description="所有节点输出")

class RetrievalResult(BaseModel):
    tenant_id: Optional[Union[int, str]] = Field(description="租户ID")
    knowledge_id: Optional[Union[int, str]] = Field(description="知识库ID")
    source: Literal["data", "doc"] = Field(description="内容来源")
    content: str = Field(description="检索内容")
    similarity_score: float = Field(description="相似度分数", ge=0.01)

class KnowledgeCallResponse(BaseModel):
    query: str = Field(default="", description="查询问题")
    retrieval_results: List[RetrievalResult] = Field(default=[], description="检索结果列表")

class KnowledgeNodeDefaultOutput(BaseModel):
    output: str = Field("输出内容")
    
class KnowledgeNodeDefaultOutputs(BaseModel):
    """知识节点默认输出schema"""
    output_list: List[KnowledgeNodeDefaultOutput] = Field(description="输出列表", serialization_alias="outputList")