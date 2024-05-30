from langchain.agents import create_openai_tools_agent, AgentExecutor
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate, ChatPromptTemplate, SystemMessagePromptTemplate, MessagesPlaceholder, HumanMessagePromptTemplate
from langchain.memory import ConversationBufferMemory

import json
from langchain.pydantic_v1 import BaseModel, Field
from langchain.tools import BaseTool, StructuredTool, tool
from langchain_core.tools import ToolException

class GetIpInfoInput(BaseModel):
    ip: str = Field(description="查询的IP地址")

def ip_info(ip: str):
    return json.dumps(
        {
            "msg": "操作成功",
            "code": 200,
            "data": {
                "id": None,
                "ip": "115.236.153.174",
                "minip": None,
                "maxip": None,
                "riskTag": None,
                "getTime": None,
                "getStartTime": None,
                "getEndTime": None,
                "riskLevel": None,
                "riskScore": None,
                "continent": None,
                "countryCode": None,
                "country": "中国",
                "province": "浙江省",
                "city": None,
                "district": None,
                "bdLon": None,
                "bdLat": None,
                "wgsLon": None,
                "wgsLat": None,
                "radius": None,
                "isp": "中国电信",
                "owner": None,
                "scene": None,
                "insertTime": None,
                "updateTime": None,
                "adcode": None,
                "timezone": None,
                "accuracy": None,
                "source": "数据中心",
                "asnumber": "58461",
                "areacode": None,
                "zipcode": None,
                "lngwgs": None,
                "latwgs": None
            }
        }
    )

def _handle_error(error: ToolException) -> str:
    return (
        "The following errors occurred during tool execution:"
        + error.args[0]
        + "Please try another tool."
    )

get_ip_info = StructuredTool.from_function(
    func=ip_info,
    name="get_ip_information",
    description="获取IP的基本信息接口，专门设计用来查询特定IP地址相关属性的服务。通过这个接口，用户可以获得一个IP地址的多种信息，包括但不限于地理位置、所属的自治系统（ASN）、运营商信息等。",
    args_schema=GetIpInfoInput,
    # return_direct=True,
    handle_tool_error=_handle_error,
)

tools = [get_ip_info]

llm = ChatOpenAI(
    model="gpt-3.5-turbo-0125",
    base_url="https://api.chatanywhere.com.cn",
    api_key="sk-Ms5F2wAkilaaZYo0HpumWR7qBLkOIsXflNQeAHSrNtmUYjzk",
    temperature=0.5,
)

prompt = ChatPromptTemplate.from_messages(
    [
        SystemMessagePromptTemplate(prompt=PromptTemplate(input_variables=[], template="你是一位聊天机器人")), 
        MessagesPlaceholder(variable_name='history', optional=True), 
        HumanMessagePromptTemplate(prompt=PromptTemplate(input_variables=['input'], template='{input}')), 
        MessagesPlaceholder(variable_name='agent_scratchpad')
    ]
)

# extra_messages =     [
#         SystemMessagePromptTemplate(prompt=PromptTemplate(input_variables=[], template="你是一位聊天机器人")), 
#         MessagesPlaceholder(variable_name='history', optional=True), 
#         HumanMessagePromptTemplate(prompt=PromptTemplate(input_variables=['input'], template='{input}')), 
#         MessagesPlaceholder(variable_name='agent_scratchpad')
# ]
# prompt = OpenAIFunctionsAgent.create_prompt(extra_prompt_messages=extra_messages)
agent= create_openai_tools_agent(
    llm=llm,
    tools=tools,
    prompt=prompt
)

# Add memory
memory = ConversationBufferMemory(human_prefix="agent", return_messages=True)
agent_executor = AgentExecutor(agent=agent, tools=tools, memory=memory, verbose=True)

print(agent_executor.invoke({"input": "我的姓名叫dcj"}))

print(agent_executor.invoke({"input": "我叫什么名字？"}))