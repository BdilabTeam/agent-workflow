from typing import Optional

from langchain.agents import AgentExecutor
from langchain.schema.memory import BaseMemory
from langchain.tools import Tool
from langchain_core.language_models import BaseLanguageModel
from langflow import CustomComponent
from langflow.components.custom_components.utils.qa_node_utils import process_agent_node


class MixAgentQa(CustomComponent):
    display_name: str = "融合问答智能体节点"
    def build_config(self):
        return {
        }

    def build(
            llm: BaseLanguageModel,
            memory: BaseMemory,
            docqa: Tool = None,
            dataqa: Tool = None,
            tableqa: Tool = None
    ) -> AgentExecutor:
        """
        在prompt字段里面
        "value": "你是一位智能助手，请按需要调用工具或者用自己的知识解决问题，用中文回答",
        """
        return process_agent_node(
            llm=llm,
            memory=memory,
            docqa=docqa,
            dataqa=dataqa,
            tableqa=tableqa,
        )
