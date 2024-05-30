from typing import List
from pydantic import BaseModel, Field, parse_obj_as

from langchain_core.tools import ToolException
from langchain.tools import StructuredTool
from langflow import CustomComponent
from langflow.field_typing import Data, Tool
from langflow.custom_schemas.agents import KnowledgeNode, KnowledgeSchema
from langchain.pydantic_v1 import BaseModel, Field


class AgentKnowledge(CustomComponent):
    display_name = "智能体知识库节点"

    def build_config(self):
        return {
            "knowledge_node": {
                "display_name": "知识库节点schema",
                "required": False,
                "field_type": "dict"
            }
        }

    def build(self, knowledge_node: KnowledgeNode) -> Tool:
        tools = []

        if knowledge_node != None:
            # 定义入参schema
            class KnowledgeInfoInput(BaseModel):
                query: str = Field(description="知识库查询语句")

            # 定义处理错误函数
            def _handle_error(error: ToolException) -> str:
                return (
                        "The following errors occurred during tool execution:"
                        + error.args[0]
                        + "Please try another tool."
                )

            try:
                knowledge_node = KnowledgeNode(**knowledge_node)
                knowledge_schemas = knowledge_node.knowledge_schemas
                i = 0

                for knowledge_schema in knowledge_schemas:
                    i = i + 1
                    id = knowledge_schema.knowledge_id
                    name = knowledge_schema.knowledge_name
                    desc = knowledge_schema.knowledge_desc

                    function_string = f"""
def knowledge_search_{i}(query: str):
    headers = None
    url = "172.22.102.61:48080/admin-api/agent/text/langFlowAskTab"
    payload = {{'query': query, 'knowledge_base_ids': '{id}' }}
    response = requests.post(url, json=payload, headers=headers)
    response_json = response.json()
    data = json.dumps(response_json.get('data').get('reference'), ensure_ascii=False)
    return data
    """

                    local_namespace = {}
                    exec(function_string, globals(), local_namespace)

                    structuredTool = StructuredTool.from_function(
                        func=local_namespace[f"knowledge_search_{i}"],
                        name=name,
                        args_schema=KnowledgeInfoInput,
                        description=desc,
                        handle_tool_error=_handle_error,
                    )

                    tools.append(structuredTool)
            except Exception as e:
                pass

        return tools
