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
    # model_name: Literal["qwen1.5-14b-chat", "gpt-3.5-turbo-0125", "gpt-3.5-turbo-1106", "gpt-4-turbo-preview", "gpt-4-0125-preview", "gpt-4-1106-preview", "gpt-4-vision-preview"] = Field(description="模型名称")
    model_name: str = Field(description="模型名称")
    model_parameters: ModelParameters = Field(description="模型配置参数")
    model_quota: ModelQuota = Field(description="模型配额指标")

class MixDocQa(BaseModel):
    """融合文档问答模型schema"""
    # query: str = Field(description="问题")
    mode: Literal[0, 1] = Field(description="模式")
    knowledge_base_ids: List[str]= Field(description="知识库id列表")
    maximum_number_of_recalls: int = Field(default=3, ge=1, le=9, description="最大召回数")
    minimum_matching_degree: float = Field(default=0.75, ge=0.01, le=0.99, description="最小相似度")
    tenant_id: Union[str, int] = Field(description="租户ID")
    search_strategy: str = Field(default="semantic", description="搜索策略")
    history: List[str] = Field(default="", description="历史对话记录")
    model_name: str = Field(description="模型名称")

class MixDataQa(BaseModel):
    tenant_id: Union[str, int] = Field(description="租户ID")
    knowledge_base_ids: List[str]= Field(description="知识库id列表")
    model_name: str = Field(description="模型名称")


class MixTableQa(BaseModel):
    tenant_id: Union[str, int] = Field(description="租户ID")
    knowledge_base_ids: List[str]= Field(description="知识库id列表")
    model_name: str = Field(description="模型名称")