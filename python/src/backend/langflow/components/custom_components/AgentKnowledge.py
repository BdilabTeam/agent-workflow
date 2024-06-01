from typing import List
from pydantic import BaseModel, Field, parse_obj_as

from langchain_core.tools import ToolException
from langchain.tools import StructuredTool
from langflow import CustomComponent
from langflow.field_typing import Data, Tool
from langflow.custom_schemas.agents import KnowledgeNode, KnowledgeSchema
from langchain.pydantic_v1 import BaseModel, Field
from utils.Agent_node_utils import process_knowledge_node

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
        """
        "value": {
                  "knowledge_schemas": [
                    {
                      "tenant_id": "1",
                      "knowledge_id": "62fdb2254f4b4de0a52d5fa0422bedd7",
                      "knowledge_desc": "用于获取网络安全相关信息",
                      "knowledge_name": "network_security"
                    }
                  ]
                },
        """
        return process_knowledge_node(knowledge_node)