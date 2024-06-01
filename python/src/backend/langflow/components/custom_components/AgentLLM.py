from typing import Optional, Union
from pydantic import BaseModel, Field, parse_obj_as

from langchain.llms import BaseLLM
from langchain_community.chat_models.openai import ChatOpenAI

from langflow import CustomComponent
from langflow.field_typing import BaseLanguageModel
from langflow.custom_schemas.agents import ModelQuota, ModelParameters, Model
from utils.Agent_node_utils import process_llm_node

class LLM(CustomComponent):
    display_name = "智能体大模型节点"

    def build_config(self):
        return {
            "model": {
                "display_name": "智能体大模型节点schema",
                "required": False,
                "field_type": "dict"
            }
        }

    def build(
            self,
            model: dict = {}
    ) -> Union[BaseLanguageModel, BaseLLM]:
        """
        "value": {
                  "data": {
                    "model_name": "qwen1.5-14b-chat",
                    "model_quota": {
                      "token_resp": 4000,
                      "token_limit": 4096,
                      "system_prompt_limit": 3276
                    },
                    "model_parameters": {
                      "temperature": 0.4,
                      "openai_api_key": "EMPTY",
                      "openai_base_url": "http://172.18.22.19:7002/v1"
                    }
                  }
                },
        """
        return process_llm_node(model)
