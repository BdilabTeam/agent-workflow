from typing import Optional, Union
from pydantic import BaseModel, Field, parse_obj_as

from langchain.llms import BaseLLM
from langchain_community.chat_models.openai import ChatOpenAI

from langflow import CustomComponent
from langflow.field_typing import BaseLanguageModel
from langflow.custom_schemas.agents import ModelQuota, ModelParameters, Model


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
        
        
        model = model["data"]
        llm = parse_obj_as(Model, model)
        model_name = llm.model_name
        temperature = llm.model_parameters.temperature
        api_key = llm.model_parameters.openai_api_key
        base_url = llm.model_parameters.openai_base_url
        token_limit =  llm.model_quota.token_limit
        token_resp = llm.model_quota.token_resp
        system_prompt_limit = llm.model_quota.system_prompt_limit
        
        return ChatOpenAI(
            model="gpt-3.5-turbo-0125",
            base_url="https://api.chatanywhere.com.cn",
            api_key="sk-Ms5F2wAkilaaZYo0HpumWR7qBLkOIsXflNQeAHSrNtmUYjzk",
            temperature=0.5,
        )

        # return ChatOpenAI(
        #     model="qwen1.5-14b-chat",
        #     base_url="http://172.18.22.19:7002/v1",
        #     api_key="EMPTY",
        #     temperature=0.5
        # )