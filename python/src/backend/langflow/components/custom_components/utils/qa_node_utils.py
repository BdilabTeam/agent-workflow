from typing import Optional, List

from pypinyin import lazy_pinyin

from langflow.field_typing import Tool
import requests

import os
from langchain.memory import ConversationTokenBufferMemory
from langchain_community.chat_models.openai import ChatOpenAI
from langchain_core.language_models import BaseLanguageModel
from langchain_core.memory import BaseMemory
from langchain_core.prompts import SystemMessagePromptTemplate, MessagesPlaceholder, PromptTemplate, \
    HumanMessagePromptTemplate, ChatPromptTemplate
from pydantic import BaseModel, Field, parse_obj_as
from langchain_core.tools import ToolException, StructuredTool
from langchain.agents import OpenAIMultiFunctionsAgent, AgentExecutor, create_openai_functions_agent, create_openai_tools_agent
from langchain_core.tools import Tool, ToolException
from pydantic import BaseModel, Field, parse_obj_as
from langchain.tools import StructuredTool
from langchain.pydantic_v1 import BaseModel, Field
from langflow.components.custom_components.utils.constants import DOC_QA_URL, DATA_QA_URL, EXCEL_QA_URL

from langflow.components.custom_components.schemas.mixqa import (
    MixDocQa, Model,
    MixDataQa, MixTableQa
)

#查询知识库入参schema
class KnowledgeInfoInput(BaseModel):
    query: str = Field(description="用户的问题")

def process_doc_qa_node(mix_doc_qa: MixDocQa) -> Tool:
    if not (doc_qa_url := os.getenv("DOC_QA_URL")):
        doc_qa_url = DOC_QA_URL
    # 定义处理错误函数
    def _handle_error(error: ToolException) -> str:
        return (
                "The following errors occurred during tool execution:"
                + error.args[0]
                + "Please try another tool."
        )

    doc_qa_param = MixDocQa(**mix_doc_qa)

    #初始化文档问答工具
    def doc_qa(question: str):
        url = doc_qa_url
        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json'
        }
        payload = {
            "query": question,
            "mode": doc_qa_param.mode,
            "knowledge_base_ids": doc_qa_param.knowledge_base_ids,
            "maximum_number_of_recalls": doc_qa_param.maximum_number_of_recalls,
            "minimum_matching_degree": doc_qa_param.minimum_matching_degree,
            "tenant_id": doc_qa_param.tenant_id,
            "search_strategy": doc_qa_param.search_strategy,
            "history": doc_qa_param.history,
            "model_name": doc_qa_param.model_name
        }
        try:
            response = requests.post(url, headers=headers, json=payload)
            if 200 <= response.status_code < 300:
                response_json = response.json()
                if response_json.get('code') == 0:
                    data = response_json.get('data')
                    if data is not None:
                        return data
                    else:
                        return "抱歉, 查询到的数据为空"
                else:
                    return "抱歉, 此工具调用失败, 请试试其它工具"
            else:
                return "抱歉，请求发送失败, 请详细描述"
        except Exception as e:
            return "抱歉, 我没有查到确切的信息, 请详细描述"


    doc_tool = StructuredTool.from_function(
        func=doc_qa,
        name="document_question_answer",
        description="针对问题查找文本文档进行回答",
        args_schema=KnowledgeInfoInput,
        handle_tool_error=_handle_error,
    )

    return doc_tool

def process_data_qa_node(mix_data_qa: MixDataQa) -> Tool:
    if not (data_qa_url := os.getenv("DATA_QA_URL")):
        data_qa_url = DATA_QA_URL

    # 定义处理错误函数
    def _handle_error(error: ToolException) -> str:
        return (
                "The following errors occurred during tool execution:"
                + error.args[0]
                + "Please try another tool."
        )

    data_qa_param = MixDataQa(**mix_data_qa)

    #初始化文档问答工具
    def data_qa(question: str):
        url = data_qa_url
        headers = {
            "accept": "application/json",
            "Content-Type": "application/json"
        }
        payload = {
            "text": question,
            "tenantId": data_qa_param.tenant_id,
            "knowledgeBaseIds": data_qa_param.knowledge_ids,
            "model_name": data_qa_param.model_name
        }
        try:
            response = requests.post(url, headers=headers, json=payload)
            if 200 <= response.status_code < 300:
                response_json = response.json()
                data = response_json.get("reference")
                display = response_json.get("display")
                if display == "0":
                    return "数据表中没有查询到相应的信息，请参考其他形式的文件"
                else:
                    return data
            else:
                return "抱歉，请求发送失败, 请详细描述"
        except Exception as e:
            return "抱歉, 我没有查到确切的信息, 请详细描述"

    data_tool = StructuredTool.from_function(
        func=data_qa,
        name="data_question_answer",
        description="针对问题查找数据库进行回答",
        args_schema=KnowledgeInfoInput,
        handle_tool_error=_handle_error
    )

    return data_tool

def process_excel_qa_node(knowledge_id: str) -> Tool:
    if not (excel_qa_url := os.getenv("EXCEL_QA_URL")):
        excel_qa_url = EXCEL_QA_URL

    # 定义处理错误函数
    def _handle_error(error: ToolException) -> str:
        return (
                "The following errors occurred during tool execution:"
                + error.args[0]
                + "Please try another tool."
        )


    #初始化文档问答工具
    def excel_qa(question: str):
        return requests.post(excel_qa_url, json={"question": question}).json()

    excel_tool = StructuredTool.from_function(
        func=excel_qa,
        name="excel_question_answer",
        description="针对问题查找表格进行回答",
        args_schema=KnowledgeInfoInput,
        handle_tool_error=_handle_error,
    )

    return excel_tool

def process_llm_node(model: dict = {}):
    model = model["data"]
    llm = parse_obj_as(Model, model)
    model_name = llm.model_name
    temperature = llm.model_parameters.temperature
    api_key = llm.model_parameters.openai_api_key
    base_url = llm.model_parameters.openai_base_url
    token_limit = llm.model_quota.token_limit
    token_resp = llm.model_quota.token_resp
    system_prompt_limit = llm.model_quota.system_prompt_limit

    return ChatOpenAI(
        model=model_name,
        base_url=base_url,
        api_key=api_key,
        temperature=temperature
    )

    # return ChatOpenAI(
    #     model="qwen1.5-14b-chat",
    #     base_url="http://124.70.213.108:7009/v1",
    #     api_key="EMPTY",
    #     temperature=0.3
    # )

    # return ChatOpenAI(
    #     model="qwen1.5-14b-chat",
    #     # model="glm-4-9-chat",
    #     # model="deepseek-coder:33b",
    #     base_url="http://172.22.102.61:3000/v1",
    #     api_key="sk-rm3ToYiJDy2MYPIf0c87Eb137f7644Dc9e84F03bD7B2F536",
    #     temperature=0.3
    # )

    # return ChatOpenAI(
    #     model="qwen2-72b",
    #     # model="qwen1.5-14b-chat-0625",
    #     base_url="http://localhost:6006/v1",
    #     api_key="EMPTY",
    #     temperature=0
    # )

    # return ChatOpenAI(
    #     model="gpt-4-turbo-preview",
    #     #  model="gpt-4-1106-preview",
    #     base_url="https://api.chatanywhere.com.cn",
    #     api_key="sk-Mj4ShXvqWIAEexqoQfBqdwjAKvFeOcVGiiXn2heC3b9bukw4",
    #     temperature=0.5,
    # )

def process_agent_node(
        llm: BaseLanguageModel,
        memory: BaseMemory,
        docqa: Tool = None,
        dataqa: Tool = None,
        tableqa: Tool = None
):
    tools = docqa + dataqa + tableqa

    system_prompt = "你是一位智能问答助手，获得用户提出的问题,依次调用文档，数据和表格问答工具进行回答。不要漏掉任何一个工具"
    if not memory:
        memory_key = "chat_history"
        memory = ConversationTokenBufferMemory(
            memory_key=memory_key,
            return_messages=True,
            output_key="output",
            llm=llm,
            max_token_limit=2000,
        )
    else:
        memory_key = memory.memory_key  # type: ignore

    prompt = ChatPromptTemplate.from_messages(
        [
            SystemMessagePromptTemplate(prompt=PromptTemplate(input_variables=[], template=system_prompt)),
            MessagesPlaceholder(variable_name='chat_history', optional=True),
            HumanMessagePromptTemplate(prompt=PromptTemplate(input_variables=['input'], template='{input}')),
            MessagesPlaceholder(variable_name='agent_scratchpad')
        ]
    )

    if llm.model_name.startswith("gpt"):
        agent = create_openai_functions_agent(llm=llm, tools=tools, prompt=prompt)
    else:
        agent = create_openai_tools_agent(llm=llm, tools=tools, prompt=prompt)
    # agent = create_openai_functions_agent(llm=llm, tools=tools, prompt=prompt)

    return AgentExecutor(
        agent=agent,
        tools=tools,  # type: ignore
        memory=memory,
        verbose=True,
        return_intermediate_steps=True,
        early_stopping_method="generate",
        handle_parsing_errors=True,
    )