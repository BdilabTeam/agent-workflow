from typing import Optional

from langchain.agents import AgentExecutor
from langchain.schema.memory import BaseMemory
from langchain.tools import Tool
from langchain_core.language_models import BaseLanguageModel
from langflow import CustomComponent
from langflow.components.custom_components.utils.agent_node_utils import process_agent_node


class ConversationalAgent(CustomComponent):
    display_name: str = "OpenAI Conversational Agent"
    description: str = "Conversational Agent that can use OpenAI's function calling API"

    def build_config(self):
        return {
        }

    def build(
            self,
            llm: BaseLanguageModel,
            memory: BaseMemory,
            system_prompt: Optional[str] = "",
            tool: Optional[Tool] = [],
            knowledge: Optional[Tool] = [],
            workflow: Optional[Tool] = [],
    ) -> AgentExecutor:
        """
        在prompt字段里面
        "value": "你是一位智能助手，请按需要调用工具或者用自己的知识解决问题，用中文回答",
        """
        return process_agent_node(
            llm=llm,
            memory=memory,
            system_prompt=system_prompt,
            tool=tool,
            knowledge=knowledge,
            workflow=workflow,
        )
