from typing import Optional

from pypinyin import lazy_pinyin

from langflow.field_typing import Tool

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
from langflow.components.custom_components.utils.constants import TOOL_CALL_URL_AGENT, KNOWLEDGE_CALL_URL_AGENT, WORKFLOW_CALL_URL_AGENT

from langflow.components.custom_components.schemas.agents import (
    ToolNode, Model,
    WorkflowNode, KnowledgeNode
)
def process_tool_node(tool_node: ToolNode) -> Tool:


    # 处理tool_node并返回Tool对象
    tools = []
    if tool_node != None:
        # 定义处理错误函数
        def _handle_error(error: ToolException) -> str:
            return (
                    "The following errors occurred during tool execution:"
                    + error.args[0]
                    + "Please try another tool."
            )

        try:
            if not (tool_call_url := os.getenv("TOOL_CALL_URL")):
                tool_call_url = TOOL_CALL_URL_AGENT
            tool_node = ToolNode(**tool_node)
            # 工具集
            tool_schemas = tool_node.tool_schemas
            i = 0

            for tool_schema in tool_schemas:
                i = i + 1
                id = tool_schema.tool_id
                name = tool_schema.tool_name
                desc = tool_schema.tool_desc
                input_schemas = tool_schema.input_schema
                tenant_id = tool_schema.tenant_id

                # 动态创建输入schema
                # fields = [(input_schema.name, input_schema.type, input_schema.desc) for input_schema in
                #           input_schemas]
                # DynamicInputSchema = create_input_schema(fields, i)

                args = ",".join([f"{input_schema.name}: {input_schema.type}" for input_schema in input_schemas])
                # func_body = "\n".join(
                #     [f"    print(f'Argument {arg['name']} ({arg['type']}):', {arg['name']})" for arg in input_schemas])

                function_string = f"""
def tool_{i}({args}):
    import json
    import requests
    url = '{tool_call_url}'
    headers = {{
        'tenant-id': '{tenant_id}',
        'Content-Type': 'application/json'
    }}
    request_body = json.dumps({{ {', '.join(f"'{input_schema.name}': {input_schema.name}" for input_schema in input_schemas)} }}, ensure_ascii=False)
    payload = {{
        'requestBody': request_body,
        'toolId': '{id}'
    }}
    try:
        response = requests.post(url, json=payload, headers=headers)
        if 200 <= response.status_code < 300:
            response_json = response.json()
            return response_json
        else:
            return "抱歉，请求发送失败, 请详细描述"
    except Exception as e:
        return "抱歉, 我没有查到确切的信息, 请详细描述"
    """

                local_namespace = {}
                exec(function_string, globals(), local_namespace)

                structuredTool = StructuredTool.from_function(
                    func=local_namespace[f"tool_{i}"],
                    # name='_'.join(lazy_pinyin(name)),
                    name=f"tool_{id}",
                    description=desc,
                    # args_schema=DynamicInputSchema,
                    handle_tool_error=_handle_error,
                )

                tools.append(structuredTool)
        except Exception as e:
            pass

    return tools

def process_workflow_node(workflow_node: WorkflowNode) -> Tool:

    tools = []

    if workflow_node != None:
        if not (workflow_call_url := os.getenv("WORKFLOW_CALL_URL")):
            workflow_call_url = WORKFLOW_CALL_URL_AGENT
        def _handle_error(error: ToolException) -> str:
            return (
                    "The following errors occurred during tool execution:"
                    + error.args[0]
                    + "Please try another tool."
            )

        try:
            # 工具集
            workflow_node = WorkflowNode(**workflow_node)
            agent_exec_id = workflow_node.agent_exec_id
            workflow_schemas = workflow_node.workflow_schemas
            i = 0

            for workflow_schema in workflow_schemas:
                i = i + 1
                id = workflow_schema.workflow_id
                name = workflow_schema.workflow_name
                desc = workflow_schema.workflow_desc
                input_schemas = workflow_schema.input_schema
                tenant_id = workflow_schema.tenant_id

                # 动态创建输入schema
                # fields = [(input_schema.name, input_schema.type, input_schema.desc) for input_schema in
                #           input_schemas]
                # DynamicInputSchema = create_input_schema(fields, i)

                args = ",".join([f"{input_schema.name}: {input_schema.type}" for input_schema in input_schemas])
                # func_body = "\n".join(
                #     [f"    print(f'Argument {arg['name']} ({arg['type']}):', {arg['name']})" for arg in input_schemas])
                function_string = f"""
def workflow_{i}({args}):
    import json
    import requests
    url = '{workflow_call_url}'
    headers = {{
        'tenant-id': '{tenant_id}',
        'Content-Type': 'application/json'
        '
    }}
    request_body = {{ {', '.join(f"'{input_schema.name}': {input_schema.name}" for input_schema in input_schemas)} }}
    payload = {{
        'workflowId': '{id}',
        'input': request_body,
        'agentExecId': '{agent_exec_id}'
    }}
    try:
        response = requests.post(url, headers=headers, json=payload)
        if 200 <= response.status_code < 300:
            response_json = response.json()
            if response_json.get('code') == 0:
                data = response_json.get('data').get('workflowResult')
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
    """

                local_namespace = {}
                exec(function_string, globals(), local_namespace)


                structuredTool = StructuredTool.from_function(
                    func=local_namespace[f"workflow_{i}"],
                    # name='_'.join(lazy_pinyin(name)),
                    name=f"workflow_{id}",
                    description=desc,
                    # args_schema=DynamicInputSchema,
                    handle_tool_error=_handle_error,
                )

                tools.append(structuredTool)

        except Exception as e:
            pass
        return tools

def process_knowledge_node(knowledge_node: KnowledgeNode) -> Tool:


    tools = []

    if knowledge_node != None:
        # 定义入参schema
        class KnowledgeInfoInput(BaseModel):
            query: str = Field(description="")

        # 定义处理错误函数
        def _handle_error(error: ToolException) -> str:
            return (
                    "The following errors occurred during tool execution:"
                    + error.args[0]
                    + "Please try another tool."
            )

        try:
            if not (knowledge_call_url := os.getenv("KNOWLEDGE_CALL_URL_AGENT")):
                knowledge_call_url = KNOWLEDGE_CALL_URL_AGENT
            knowledge_node = KnowledgeNode(**knowledge_node)
            knowledge_schemas = knowledge_node.knowledge_schemas
            i = 0

            for knowledge_schema in knowledge_schemas:
                i = i + 1
                id = knowledge_schema.knowledge_id
                name = knowledge_schema.knowledge_name
                desc = knowledge_schema.knowledge_desc
                tenant_id = knowledge_schema.tenant_id

                function_string = f"""
def knowledge_search_{i}(query: str):
    import requests
    import json
    url = '{knowledge_call_url}'
    headers = {{
        'tenant-id': '{tenant_id}',
        'Content-Type': 'application/json'
    }}
    payload = {{'query': query, 'knowledge_base_id': '{id}' }}
    response = requests.post(url, json=payload, headers=headers)
    response_json = response.json()
    data = response_json.get('reference')
    return data
    """

                local_namespace = {}
                exec(function_string, globals(), local_namespace)

                structuredTool = StructuredTool.from_function(
                    func=local_namespace[f"knowledge_search_{i}"],
                    # name='_'.join(lazy_pinyin(name)),
                    name=f"knowledge_{id}",
                    args_schema=KnowledgeInfoInput,
                    description=desc,
                    handle_tool_error=_handle_error,
                )

                tools.append(structuredTool)
        except Exception as e:
            pass

    return tools

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
        system_prompt: Optional[str] = "",
        tool: Optional[Tool] = [],
        knowledge: Optional[Tool] = [],
        workflow: Optional[Tool] = [],
):
    tools = tool + knowledge + workflow

    if system_prompt == "":
        system_prompt = """
            你是一位智能助手，请通过你自己的知识和调用工具解决问题,全部回答请用中文。
                注意：
                1.如果可以调用工具解决，请调用工具，如果不可以则用自己的理解回答。
            """
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