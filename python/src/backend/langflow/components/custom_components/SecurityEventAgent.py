# from langflow import CustomComponent
# from langflow.field_typing import Data

# import re
# import json
# import asyncio
# import operator
# from typing import List, Tuple, Annotated, TypedDict

# from langchain.pydantic_v1 import BaseModel, Field
# from langchain.tools import StructuredTool
# from langchain_core.tools import ToolException
# from langchain_core.pydantic_v1 import BaseModel
# from langchain_core.prompts import ChatPromptTemplate
# from langchain_openai import ChatOpenAI
# from langchain.agents import create_openai_tools_agent, AgentExecutor, initialize_agent, AgentType
# from langchain_openai import ChatOpenAI
# from langchain.prompts import PromptTemplate, ChatPromptTemplate, SystemMessagePromptTemplate, MessagesPlaceholder, HumanMessagePromptTemplate
# from langchain.memory import ConversationBufferMemory


# from langgraph.prebuilt import create_agent_executor
# from langgraph.prebuilt.chat_agent_executor import create_tool_calling_executor
# from langgraph.graph import StateGraph, END
# from langgraph.graph.graph import CompiledGraph



# class SecurityEventAgent(CustomComponent):
#     display_name = "智能研判Agent"
#     documentation: str = "http://docs.langflow.org/components/custom"

#     def build_config(self):
#         return {"event": {"display_name": "安全事件"}}

#     def build(self, event: str) -> Data:
#         class GetIpInfoInput(BaseModel):
#             ip: str = Field(description="查询的IP地址")

#         def ip_info(ip: str):
#             return json.dumps(
#                 {
#                     "msg": "操作成功",
#                     "code": 200,
#                     "data": {
#                         "id": None,
#                         "ip": "115.236.153.174",
#                         "minip": None,
#                         "maxip": None,
#                         "riskTag": None,
#                         "getTime": None,
#                         "getStartTime": None,
#                         "getEndTime": None,
#                         "riskLevel": None,
#                         "riskScore": None,
#                         "continent": None,
#                         "countryCode": None,
#                         "country": "中国",
#                         "province": "浙江省",
#                         "city": None,
#                         "district": None,
#                         "bdLon": None,
#                         "bdLat": None,
#                         "wgsLon": None,
#                         "wgsLat": None,
#                         "radius": None,
#                         "isp": "中国电信",
#                         "owner": None,
#                         "scene": None,
#                         "insertTime": None,
#                         "updateTime": None,
#                         "adcode": None,
#                         "timezone": None,
#                         "accuracy": None,
#                         "source": "数据中心",
#                         "asnumber": "58461",
#                         "areacode": None,
#                         "zipcode": None,
#                         "lngwgs": None,
#                         "latwgs": None
#                     }
#                 }
#             )
        
#         class TrapDetectionInfoInput(BaseModel):
#             value: str = Field(description="查询值，可以是IP地址、域名或其他类型的查询项，用于检索与之相关的情报数据。")
        
#         # def trap_detection_info(page_num: int, page_size: int, value: str):
#         def trap_detection_info(value: str):
#             return json.dumps(
#                 {
#                     "total": 1,
#                     "rows": [
#                         {
#                             "id": "13f4bfda2dd05df7dc5c9afd97c350c4a5f4387e15b0ccda77b333c5c85d11d3",
#                             "iocKey": "115.236.153.174",
#                             "ioc1": "115.236.153.174",
#                             "ioc2": "53413",
#                             "ioc3": "",
#                             "iocCategory": "ip",
#                             "protocol": "",
#                             "maliciousType": "远控木马",
#                             "malwareFamily": "Dorkbot",
#                             "isApt": False,
#                             "campaign": "",
#                             "aptGroup": "",
#                             "killChain": [
#                                 ""
#                             ],
#                             "alertName": "Dorkbot远控木马活动事件",
#                             "platform": [
#                                 "Windows"
#                             ],
#                             "risk": "high",
#                             "confidence": "high",
#                             "currentStatus": "unknown",
#                             "ttp": "MD5:5676b9d26ab3441d81ef904d60902207Size:2014208FileType:PE32ExePlatform:WINDOWSProcessPath:C:\\Users\\ADMINI~1\\AppData\\Local\\Temp\\svshoct.exePE_Timestamp:2013-01-0918:36:49DNS:TCP:115.236.153.174:1937660.167.153.43:2979HTTP::family:md5:17ec6f6cb75d2afeb72ea848fa78e15epayload:------------------------------------------------------------------------|000102030405060708090A0B0C0D0E0FDump------------------------------------------------------------------------|6e6e1facffffffbffcfffffdffffff779bnn.............w.|5c5f5f97fcc36b3fcb07c314621617977f\\__...k?....b....|6f654e56616da53d3f5d6db17d1efcdafeoeNVam.=?]m.}....|975f9394cbbebfbffd12541cbf570ee9e6._........T..W...|e416e16566e6120ddd15674178800afdbf...ef.....gAx....|c381bf3ff620c8bfef228f8abe22322aae...?....\"...\"2*.|a083030c0bc9bb2e37b2ce6ff4321bed81........7..o.2...|0177f298b4a03f7d6a2f5f635f63ab645f.w....?}j/_c_c.d_|64679f5f6367625f45578058a788081611dg._cgb_EW.X.....|3cdfdce7a06f6fcad9c4e7ddff78f80000<....oo......x...md5:17ec6f6cb75d2afeb72ea848fa78e15efilename:\"-\"size:506880type:PE32ExecutableforMSWindowsfirst_seen:2023-06-1021:05:05processpath:-cmdline:-pe_timestamp:2022-05-0423:27:12family:-susp_family:-malicious_type:-",
#                             "description": "",
#                             "tags": [
#                                 "远控木马",
#                                 "白名单"
#                             ],
#                             "insertTime": "2023-07-28 18:51:43",
#                             "updateTime": None,
#                             "createdTime": "2023-09-08 17:20:04",
#                             "createdBy": "admin",
#                             "updatedTime": None,
#                             "updatedBy": None
#                         }
#                     ],
#                     "code": 200,
#                     "msg": "查询成功"
#                 }
#             )
        
#         class OwnDetectionInfoInput(BaseModel):
#             value: str = Field(description="查询值可以是IP地址、域名或其他类型的查询项，用于检索与之相关的情报数据。")
        
#         def own_detection_info(value: str):
#             return json.dumps(
#                 {
#                     "total": 1,
#                     "rows": [
#                         {
#                             "tags": [
#                                 "远控木马",
#                                 "白名单"
#                             ],
#                             "insertTime": "2023-09-08 17:20:04",
#                             "updateTime": "2023-09-26 10:23:05",
#                             "status": "有效"
#                         }
#                     ],
#                     "code": 200,
#                     "msg": "查询成功"
#                 }
#             )
        
#         def judgment_rules():
#             return """1.研判结果为忽略，包括：\
#             1）白名单地址：包括各漏洞扫描挖掘团队及集团的扫描器地址以及其他单位提交申请的联通自用IP。\
#             2）动态地址：未攻击成功的宽带、基站地址。\
#             3）特定IP地址：如跳板机地址和监控地址，这些地址在特定情况下可以忽略。\
#         2.研判结果为排查，包括：\
#             1）联通自用地址：攻击源为联通资产地址，需要经过事件截图分析其行为及特征后，定位到具体归属并下发相关单位或团队排查处置。\
#             2）内网IP地址：涉及特定网段的内网IP地址，需要根据归属进行排查。\
#             3）家庭宽带、基站攻击：攻击地址为联通家庭宽带、基站地址，需要通过事件截图中的攻击行为及特征进行分析后，协调归属单位进行处置。\
#         3.研判结果为封堵，包括：\
#             1）非联通自用IP：运营商归属联通，使用者非联通，在威胁情报平台被标记为恶意或者存在威胁的IP。\
#             2）非联通地址：运营商归属非联通，有扫描及攻击行为的IP。\
#             3）境外IP：非联通使用、与联通业务无关的IP。\
#             4）对联通有大量扫描和攻击行为的地址：确认过滤各扫描团队的IP之后，对联通自用IP协调归属地单位进行排查处置；非联通自用IP，立即进行封堵。\
#             5）多个分子公司上报的同一个地址：多个单位上报同一个地址，经过事件截图分析其行为以及特征之后，过滤扫描团队IP，联通自用IP协调归属地单位进行排查处置，非联通自用IP，立即进行封堵。\
#             6）部分家庭宽带及动态IP：非联通地址可封堵，联通地址经过事件截图分析其行为以及特征之后，确认为恶意IP，并且查到相关备案信息非联通自用可封堵。\
#         """
        
#         def _handle_error(error: ToolException) -> str:
#             return (
#                 "The following errors occurred during tool execution:"
#                 + error.args[0]
#                 + "Please try another tool."
#             )
        
#         get_ip_info = StructuredTool.from_function(
#             func=ip_info,
#             name="get_ip_information",
#             description="获取IP的基本信息接口，专门设计用来查询特定IP地址相关属性的服务。通过这个接口，用户可以获得一个IP地址的多种信息，包括但不限于地理位置、所属的自治系统（ASN）、运营商信息等。",
#             args_schema=GetIpInfoInput,
#             # return_direct=True,
#             handle_tool_error=_handle_error,
#         )
#         get_trap_detection_info = StructuredTool.from_function(
#             func=trap_detection_info,
#             name="get_trap_detection_info",
#             args_schema=TrapDetectionInfoInput,
#             description="详细的情报信息查询接口，专用于检测网络是否存在失陷情况，此接口可以确定某个IP地址、域名或URL是否与已知的恶意活动相关联。",
#             # return_direct=True,
#             handle_tool_error=_handle_error,
#         )
#         get_own_detection_info = StructuredTool.from_function(
#             func=own_detection_info,
#             name="get_own_detection_info",
#             args_schema=OwnDetectionInfoInput,
#             description="简洁明了的情报信息查询接口，专用于检测网络是否存在失陷情况，此接口可以确定某个IP地址、域名或URL是否与已知的恶意活动相关联。",
#             handle_tool_error=_handle_error,
#         )
#         get_judgment_rules = StructuredTool.from_function(
#             func=judgment_rules,
#             name="get_judgment_rules",
#             description="获取研判规则，返回值是详细的研判规则。",
#             handle_tool_error=_handle_error,
#         )
        
#         # Graph State
#         class ReWOO(TypedDict):
#             task: str
#             plan_string: str
#             steps: List
#             results: dict
#             result: str
        
#         # Planner
#         prompt = """你是安全事件研判助理，根据研判规则分析安全事件并得出结果。\
#         针对以下安全事件，制定可逐步解决问题的计划。针对每个计划，指出使用哪种外部工具和工具输入来检索证据。 \
#         变量#E可以被以后的工具调用。(计划, #E1, 计划, #E2, 计划 ...)
        
#         工具可以是以下工具之一:
#         (1) getIpInformation[input]: 获取IP的基本信息接口，专门设计用来查询特定IP地址相关属性的服务。通过这个接口，用户可以获得一个IP地址的多种信息，包括但不限于地理位置、所属的自治系统（ASN）、运营商信息等。
#         (2) getTrapDetectionInfo[input]: 详细的情报信息查询接口，专用于检测网络是否存在失陷情况，此接口可以确定某个IP地址、域名或URL是否与已知的恶意活动相关联。
#         (3) getOwnDetectionInfo[input]: 简洁明了的情报信息查询接口，专用于检测网络是否存在失陷情况，此接口可以确定某个IP地址、域名或URL是否与已知的恶意活动相关联。
#         (4) getGudgmentRules[input]: 获取研判规则接口，返回值是详细的研判规则。
        
#         举例：
#         安全事件: '事件描述': '119.260.113.74 Attack 60.78.180.99', '事件详情': '扫描攻击', '攻击者ip': '119.260.113.74', '被攻击者ip': '60.78.180.99'
#         计划: 查询攻击者的IP详细信息. #E1 = getIpInformation['119.260.113.74']
#         计划: 确定攻击者的IP地址是否与任何已知的恶意活动相关联. #E2 = getTrapDetectionInfo['119.260.113.74']
#         计划: 查询受害者IP详细信息. #E3 = getIpInformation['60.78.180.99']
#         计划: 确定受害者的IP地址是否与任何已知的恶意活动相关联. #E4 = getTrapDetectionInfo['60.78.180.99']
#         计划: 分析扫描攻击. #E5 = getOwnDetectionInfo['115.236.153.174']
#         计划: 获取研判规则，得出研判结果. #E6 = getGudgmentRules['']
        
#         安全事件: {task}"""
        
#         # Regex to match expressions of the form E#... = ...[...]
#         regex_pattern = r"Plan:\s*(.+)\s*(#E\d+)\s*=\s*(\w+)\s*\[([^\]]+)\]"
#         prompt_template = ChatPromptTemplate.from_messages([("user", prompt)])
#         model = ChatOpenAI(temperature=0, api_key="sk-kUx6CDr4B0Elct2aq015N9tyu6siuSxsMrS0j4g86Ssf3w1l", base_url="https://api.chatanywhere.com.cn")
        
#         planner = prompt_template | model
        
#         # Planner Node
#         # Regex to match expressions of the form E#... = ...[...]
#         regex_pattern = r"计划:\s*(.+)\s*(#E\d+)\s*=\s*(\w+)\s*\[([^\]]+)\]"
#         prompt_template = ChatPromptTemplate.from_messages([("user", prompt)])
#         planner = prompt_template | model
        
        
#         def get_plan(state: ReWOO):
#             task = state["task"]
#             result = planner.invoke({"task": task})
#             # Find all matches in the sample text
#             matches = re.findall(regex_pattern, result.content)
#             return {"steps": matches, "plan_string": result.content}
            
#         # Executor
#         def _get_current_task(state: ReWOO):
#             if state["results"] is None:
#                 return 1
#             if len(state["results"]) == len(state["steps"]):
#                 return None
#             else:
#                 return len(state["results"]) + 1
        
        
#         def tool_execution(state: ReWOO):
#             """Worker node that executes the tools of a given plan."""
#             _step = _get_current_task(state)
            
#             # Human in the loop
#             # user_response = input(f"[y/n] continue with: {state['steps'][_step - 1]}?")
#             # if user_response == "n":
#             #     raise ValueError
            
#             _, step_name, tool, tool_input = state["steps"][_step - 1]
#             _results = state["results"] or {}
#             for k, v in _results.items():
#                 tool_input = tool_input.replace(k, v)
#             if tool == "getIpInformation":
#                 result = get_ip_info.invoke(tool_input)
#             elif tool == "getTrapDetectionInfo":
#                 result = get_trap_detection_info.invoke(tool_input)
#             elif tool == "getOwnDetectionInfo":
#                 result = get_own_detection_info.invoke(tool_input)
#             elif tool == "getGudgmentRules":
#                 result = get_judgment_rules.invoke(tool_input)
#             else:
#                 raise ValueError
#             _results[step_name] = str(result)
#             return {"results": _results}
        
#         # Solver
#         solve_prompt = """你是一位安全事件研判总结助手，为了获取研判总结，我们获取了安全事件分析计划以及每一个计划检索到的证据。\
#         请谨慎使用，因为冗长的证据可能包含不相关的信息。\
#         安全事件分析计划及证据:
#         {plan}
        
#         现在根据上面提供的证据总结一份研判工单，研判工单是json blob格式，应该包括一个显式的研判结果（排查、封堵、忽略）和与该研判结果相关联的信息；\
#         若研判结果为排查，研判工单应包括：风险等级、攻击类型、排查报告、研判说明；\
#         若研判结果为忽略，研判工单包括：研判说明；\
#         若研判结果为封堵，研判工单包括：风险等级、攻击类型、研判说明。
        
#         研判工单:"""
        
        
#         def solve(state: ReWOO):
#             plan = ""
#             for _plan, step_name, tool, tool_input in state["steps"]:
#                 _results = state["results"] or {}
#                 for k, v in _results.items():
#                     tool_input = tool_input.replace(k, v)
#                     step_name = step_name.replace(k, v)
#                 plan += f"Plan: {_plan}\n{step_name} = {tool}[{tool_input}]"
#             prompt = solve_prompt.format(plan=plan)
#             result = model.invoke(prompt)
#             return {"result": result}
        
#         # Define Graph
#         def _route(state):
#             _step = _get_current_task(state)
#             if _step is None:
#                 # We have executed all tasks
#                 return "solve"
#             else:
#                 # We are still executing tasks, loop back to the "tool" node
#                 return "tool"
        
#         graph = StateGraph(ReWOO)
#         graph.add_node("plan", get_plan)
#         graph.add_node("tool", tool_execution)
#         graph.add_node("solve", solve)
#         graph.add_edge("plan", "tool")
#         graph.add_edge("solve", END)
#         graph.add_conditional_edges("tool", _route)
#         graph.set_entry_point("plan")
        
#         app = graph.compile()
        
#         outputs = []
#         try:
#             for s in app.stream({"task": event}, stream_mode="updates"):
#                 outputs.append(s)
#                 # Human in the loop
#                 user_response = input(f"[y/n] Continue with {s}?")
#                 if user_response == "n":
#                     raise ValueError
#         except:
#             return {"output": outputs}
        
#         return {"output": outputs}