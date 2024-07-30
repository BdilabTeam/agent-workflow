import os
import time
import json
import httpx
import concurrent
import concurrent.futures
from loguru import logger
from typing import List, Dict, Union
from langflow.components.custom_components.schemas.workflow import StartNode, StartNodeResponse, NodeData, TokenAndCost
from langflow.components.custom_components.utils import (
    format_prenodes_data,
    format_input_schemas_to_dict, 
    NodeType,
    compute_tokens_by_transformers,
    format_tokens,
    on_start,
    on_end,
    format_output_schemas_to_dict,
    safe_format_prompt,
    get_query_value,
    get_top_n_retrieval_results, 
    RetrievalResultSourceType
)
# Tool
from langflow.components.custom_components.schemas.workflow import ToolNode, ToolNodeResponse, NodeData, TokenAndCost
from langflow.components.custom_components.utils.constants import TOOL_CALL_URL
from langflow.components.custom_components.rest import RESTClientObject, Configuration, RESTResponse

# LLM
from langflow.components.custom_components.schemas.workflow import LLMNode, LLMNodeResponse, NodeData, TokenAndCost
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

# Knowledge
from langflow.components.custom_components.utils.constants import KNOWLEDGE_CALL_URL
from langflow.components.custom_components.schemas.workflow import (
    KnowledgeNode, 
    KnowledgeNodeResponse, 
    NodeData, 
    TokenAndCost,
    KnowledgeCallResponse,
    KnowledgeNodeDefaultOutput,
    KnowledgeNodeDefaultOutputs
)
# Workflow
from langflow.components.custom_components.schemas.workflow import WorkflowNode, WorkflowResponse, NodeData, TokenAndCost
from langflow.components.custom_components.utils.constants import WORKFLOW_CALL_URL
# End
from langflow.components.custom_components.schemas.workflow import EndNode, EndNodeResponse, NodeData, TokenAndCost

def process_start_node(start_node_schema: StartNode):
    start_time = time.time()

    # 校验node schema
    start_node_schema = StartNode(**start_node_schema)
    
    # 初始化节点状态
    start_node_data = NodeData(
        node_type=NodeType.START.value,
        node_status="RUNNING",
    )
    try:
        start_node_data.node_id = start_node_schema.node_id
        start_node_data.node_name = start_node_schema.node_name
        workflow_id = start_node_schema.flow_id
        
        # 数据库同步节点状态
        on_start(
            workflow_id=workflow_id,
            node_data=start_node_data
        )
        
        # 解析输入schema
        parsed_input_dict = format_input_schemas_to_dict(
            input_schema=start_node_schema.input_schema,
        )
        if not parsed_input_dict:
            parsed_input_json_str = ""
        else:
            parsed_input_json_str = json.dumps(parsed_input_dict, ensure_ascii=False)
        start_node_data.input = parsed_input_json_str
        
        parsed_output_json_str = parsed_input_json_str
        start_node_data.output = parsed_output_json_str
        
        # 计算token消耗
        input_tokens = compute_tokens_by_transformers(text=parsed_input_json_str)
        output_tokens = input_tokens
        total_tokens = input_tokens + output_tokens
        token_and_cost = TokenAndCost(
            input_tokens=format_tokens(input_tokens),
            output_tokens=format_tokens(output_tokens),
            total_tokens=format_tokens(total_tokens)
        )
        start_node_data.token_and_cost = token_and_cost
        
        # 节点运行成功
        node_status = "SUCCESS"
    except Exception as e:
        error_info = str(e)
        node_status = "FAILED"
        start_node_data.error_info = error_info
    
    # 更新状态
    start_node_data.node_status = node_status
    
    # 计算节点运行时间
    end_time = time.time()
    node_exe_cost = f"{round((end_time - start_time), 3)}s"
    start_node_data.node_exe_cost = node_exe_cost

    # 数据库同步节点状态
    on_end(
        workflow_id=workflow_id,
        node_data=start_node_data
    )
    
    start_node_response = StartNodeResponse(node_data=start_node_data)
    return start_node_response.model_dump()

async def aprocess_tool_node(
    prenode_inputs: List[Dict],
    tool_node_schema: ToolNode
):
    start_time = time.time()
    
    # 校验node schema
    tool_node_schema = ToolNode(**tool_node_schema)
    
    # 初始化节点状态
    tool_node_data = NodeData(
        node_type=NodeType.TOOL.value,
        node_status="RUNNING",
    )
    try:
        tool_node_data.node_id = tool_node_schema.node_id
        tool_node_data.node_name = tool_node_schema.node_name
        workflow_id = tool_node_schema.flow_id
        
        # 数据库同步节点状态
        on_start(
            workflow_id=workflow_id,
            node_data=tool_node_data
        )
        
        # 格式化前置节点输入数据
        all_nodes_data = format_prenodes_data(prenode_inputs=prenode_inputs)
        # 解析输入schema
        parsed_input_dict = format_input_schemas_to_dict(
            input_schema=tool_node_schema.input_schema,
            prenode_results=all_nodes_data
        )
        if not parsed_input_dict:
            parsed_input_json_str = ""
        else:
            parsed_input_json_str = json.dumps(parsed_input_dict, ensure_ascii=False)
        tool_node_data.input = parsed_input_json_str
        
        tool_ids = tool_node_schema.tool_ids
        tenant_id = tool_node_schema.tenant_id
        
        # # 外网接口测试
        # configuration = Configuration()
        # rest_client = RESTClientObject(configuration=configuration)
        
        # tool_call_results = []

        # for tool_id in tool_ids:
        #     tool_call_url = TOOL_CALL_URL_FORMAT.format(
        #         protocol, host
        #     )
        #     tool_call_url = "http://60.204.186.96:31185/api/v1/experiment/cards"
        #     with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        #         future = executor.submit(rest_client.GET, url=tool_call_url)
        #         tool_call_response: RESTResponse = future.result()
        #         if tool_call_response.status >= 200 and tool_call_response.status < 300:
        #             tool_call_results.append({tool_id: tool_call_response.data.decode('utf-8')})
        #         else:
        #              tool_call_results.append({tool_id: tool_call_response.reason})
        
        # mock_data = {
        #     "data": {
        #         "url": tool_call_url,
        #         "headers": headers,
        #         "body": body
        #     }
        # }

        # tool_call_results.append({tool_id: mock_data})
        
        # production test
        headers = {"tenant-id": tenant_id}
        body = {
            "requestBody": parsed_input_json_str
        }
        
        tool_call_results = []
        for tool_id in tool_ids:
            body.update({"toolId": tool_id})
            if not (tool_call_url := os.getenv("TOOL_CALL_URL")):
                tool_call_url = TOOL_CALL_URL   # 向后兼容
                
            try:
                async with httpx.AsyncClient() as client:
                    tool_call_response = await client.post(url=tool_call_url, headers=headers, json=body, timeout=15)
                    
                    if tool_call_response.is_success:
                        tool_call_results.append({tool_id: tool_call_response.json()})
                    else:
                        raise ValueError(f"工具调用响应状态异常, 状态码: {tool_call_response.status_code}")
            except httpx.TimeoutException:
                raise ValueError("工具调用请求超时")
            except httpx.HTTPStatusError as e:
                raise ValueError(f"工具调用请求状态异常, 状态码: {e.response.status_code}") from e
            except:
                raise
        
        # TODO 工具节点一次只调用一个工具
        raw_output = tool_call_results[0].get(tool_ids[0], "")
        parsed_output_json_str = json.dumps(raw_output, ensure_ascii=False)
        tool_node_data.output = parsed_output_json_str
        
        # 计算token消耗
        input_tokens = compute_tokens_by_transformers(text=parsed_input_json_str)
        output_tokens = compute_tokens_by_transformers(text=parsed_output_json_str)
        total_tokens = input_tokens + output_tokens
        token_and_cost = TokenAndCost(
            input_tokens=format_tokens(input_tokens),
            output_tokens=format_tokens(output_tokens),
            total_tokens=format_tokens(total_tokens)
        )
        tool_node_data.token_and_cost = token_and_cost
        
        node_status = "SUCCESS"
    except Exception as e:
        node_status = "FAILED"
        error_info = str(e)
        tool_node_data.error_info = error_info
            
    # 更新状态
    tool_node_data.node_status = node_status
    
    # 计算节点运行时间
    end_time = time.time()
    node_exe_cost = f"{round((end_time - start_time), 3)}s" 
    tool_node_data.node_exe_cost = node_exe_cost
        
    # 数据库同步节点状态
    on_end(
        workflow_id=workflow_id,
        node_data=tool_node_data
    )
    tool_node_response = ToolNodeResponse(node_data=tool_node_data)
    
    next_response = {"prenode_inputs": prenode_inputs}
    next_response.update(tool_node_response.model_dump())
    return next_response

async def aprocess_llm_node(
    prenode_inputs: List[Dict],
    llm_node_schema: LLMNode
):
    start_time = time.time()
    
    # 校验node schema
    llm_node_schema = LLMNode(**llm_node_schema)
    
    # 初始化节点状态
    llm_node_data = NodeData(
        node_type=NodeType.LLM.value,
        node_status="RUNNING",
    )
    try:
        llm_node_data.node_id = llm_node_schema.node_id
        llm_node_data.node_name = llm_node_schema.node_name
        workflow_id = llm_node_schema.flow_id
        
        # 数据库同步节点状态
        on_start(
            workflow_id=workflow_id,
            node_data=llm_node_data
        )
        
        # 格式化前置节点输入数据
        all_nodes_data = format_prenodes_data(prenode_inputs=prenode_inputs)
        # 解析输入schema
        parsed_input_dict = format_input_schemas_to_dict(
            input_schema=llm_node_schema.input_schema,
            prenode_results=all_nodes_data
        )
        if not parsed_input_dict:
            parsed_input_json_str = ""
        else:
            parsed_input_json_str = json.dumps(parsed_input_dict, ensure_ascii=False)
        llm_node_data.input = parsed_input_json_str
        
        if not (prompt_template := llm_node_schema.prompt):
            raise ValueError("大模型提示词'prompt'不能为空.")
        
        # 参数填充提示词模版
        formatted_prompt = safe_format_prompt(template=prompt_template, params_dict=parsed_input_dict)
        # formatted_prompt = render(template=prompt_template, data=parsed_input_dict)
        prompt_template = ChatPromptTemplate.from_messages(
            [
                ("user", formatted_prompt)
            ],
            template_format="mustache"
        )
        
        # 生产环境测试            
        model = ChatOpenAI(
            model=llm_node_schema.model_schema.model_name.lower(),
            temperature=llm_node_schema.model_schema.model_parameters.temperature,
            base_url=llm_node_schema.model_schema.model_parameters.openai_base_url,
            api_key=llm_node_schema.model_schema.model_parameters.openai_api_key,
        )
        # 外网测试
        # model = ChatOpenAI(
        #     base_url="https://api.chatanywhere.com.cn",
        #     api_key="sk-Ms5F2wAkilaaZYo0HpumWR7qBLkOIsXflNQeAHSrNtmUYjzk",
        # )
        
        chain = prompt_template | model
        # raw_output = chain.invoke({}).content
        llm_output = await chain.ainvoke({})
        raw_output = llm_output.content
        llm_node_data.raw_output = raw_output
        
        # TODO 是否需要输出解析器来解析大模型输出为用户指定数据类型？
        parsed_output_dict = format_output_schemas_to_dict(output_schema=llm_node_schema.output_schema, raw_output=raw_output)
        parsed_output_json_str = json.dumps(parsed_output_dict, ensure_ascii=False)
        llm_node_data.output = parsed_output_json_str
        
        # 计算token消耗
        input_tokens = compute_tokens_by_transformers(text=parsed_input_json_str)
        output_tokens = compute_tokens_by_transformers(text=parsed_output_json_str)
        total_tokens = input_tokens + output_tokens
        token_and_cost = TokenAndCost(
            input_tokens=format_tokens(input_tokens),
            output_tokens=format_tokens(output_tokens),
            total_tokens=format_tokens(total_tokens)
        )
        llm_node_data.token_and_cost = token_and_cost
        
        node_status = "SUCCESS"
    except Exception as e:
        node_status = "FAILED"
        error_info = str(e)
        llm_node_data.error_info = error_info
            
    # 更新状态
    llm_node_data.node_status = node_status
        
    # 计算节点运行时间
    end_time = time.time()
    node_exe_cost = f"{round((end_time - start_time), 3)}s"
    llm_node_data.node_exe_cost = node_exe_cost
        
    # 数据库同步节点状态
    on_end(
        workflow_id=workflow_id,
        node_data=llm_node_data
    )
    
    llm_node_response = LLMNodeResponse(node_data=llm_node_data)
    
    next_response = {"prenode_inputs": prenode_inputs}
    next_response.update(llm_node_response.model_dump())
    
    return next_response

async def aprocess_knowledge_node(
    prenode_inputs: List[Dict],
    knowledge_node_schema: KnowledgeNode
):
    start_time = time.time()
    
    # 校验node schema
    knowledge_node_schema = KnowledgeNode(**knowledge_node_schema)
    
    # 初始化节点状态
    knowledge_node_data = NodeData(
        node_type=NodeType.KNOWLEDGE.value,
        node_status="RUNNING",
    )
    try:
        knowledge_node_data.node_id = knowledge_node_schema.node_id
        knowledge_node_data.node_name = knowledge_node_schema.node_name
        workflow_id = knowledge_node_schema.flow_id
        
        # 数据库同步节点状态
        on_start(
            workflow_id=workflow_id,
            node_data=knowledge_node_data
        )
        
        # 格式化前置节点输入数据
        all_nodes_data = format_prenodes_data(prenode_inputs=prenode_inputs)
        # 解析输入schema
        parsed_input_dict = format_input_schemas_to_dict(
            input_schema=knowledge_node_schema.input_schema,
            prenode_results=all_nodes_data
        )
        if not parsed_input_dict:
            parsed_input_json_str = ""
        else:
            parsed_input_json_str = json.dumps(parsed_input_dict, ensure_ascii=False)
        knowledge_node_data.input = parsed_input_json_str
        
        query = get_query_value(parsed_input_dict)
        
        knowledge_ids = knowledge_node_schema.knowledge_ids
        tenant_id = knowledge_node_schema.tenant_id
        search_strategy = knowledge_node_schema.knowledge_schema.knowledge_config.search_strategy
        maximum_number_of_recalls = knowledge_node_schema.knowledge_schema.knowledge_config.maximum_number_of_recalls
        minimum_matching_degree = knowledge_node_schema.knowledge_schema.knowledge_config.minimum_matching_degree
        
        body = {
            "query": query,
            "knowledge_base_ids": knowledge_ids,
            "maximum_number_of_recalls": maximum_number_of_recalls,
            "minimum_matching_degree": minimum_matching_degree,
            "search_strategy": search_strategy,
            "tenant_id": tenant_id
        }
        
        if not (knowledge_call_url := os.getenv("KNOWLEDGE_CALL_URL")):
            knowledge_call_url = KNOWLEDGE_CALL_URL
            
        try:
            async with httpx.AsyncClient() as client:
                knowledge_call_response = await client.post(url=knowledge_call_url, json=body, timeout=20)
                if knowledge_call_response.is_success:
                    # 解析响应数据
                    knowledge_call_response_dict = knowledge_call_response.json()
                    response_code = knowledge_call_response_dict.get("code")
                    response_msg = knowledge_call_response_dict.get("msg")
                    if response_code != 0:
                        raise ValueError(f"知识库检索失败，具体原因: {response_msg}")
                    if not (response_data := knowledge_call_response_dict.get("data")):
                        raise ValueError(f"知识库检索结果为空")
                else:
                    raise ValueError(f"知识库调用响应状态异常, 状态码: {knowledge_call_response.status_code}")
        except httpx.TimeoutException:
            raise ValueError("知识库调用请求超时")
        except httpx.HTTPStatusError as e:
            raise ValueError(f"知识库调用请求状态异常, 状态码: {e.response.status_code}") from e
        except:
            raise

        # 构造响应数据用于测试
        # response_data = {
        #     "retrieval_results": [
        #         {
        #             "tenant_id": "1",
        #             "source": "doc",
        #             "knowledge_id": "54db9bf6fbef4489831b032a353e0592",
        #             "similarity_score": 0.9344667,
        #             "content": "{\"metadata\":{\"titles_new\":\"#定义：网络中开放的与安全相关的端口，这些端口或极易被黑客利用，或能直接导致安全漏洞。\",\"filetype\":\"application/vnd.openxmlformats-officedocument.wordprocessingml.document\",\"emphasized_text_tags\":[\"b\",\"b\",\"b\"],\"filename\":\"b3512ea114464f6b915f720419c07050-安全专线常见定义_V1.1.docx\",\"raw_page_content\":\"端口 列表 端口说明 21 ftp默认端口号，利用FTP服务因配置不当可能存在弱口令破解，或被木马利。处理建议：在不影响正常业务的情况下，建议关闭对外开放或者防止匿名登录。 22 ssh默认端口号，此端口开放容易被爆破，弱口令进入系统。处理建议：在不影响正常业务的情况下，建议限制登录方式或采取强密码策略。 23 Telnet默认端口号，利用Telnet服务，可搜索远程登录Unix服务，扫描操作系统类型。存在提升权限、拒绝服务等漏洞，可使远程服务器崩溃。处理建议：在不影响正常业务的情况下建议关闭或者增加访问策略。 25 利用25端口，可寻找SMTP服务器，转发垃圾邮件。被多数木马程序利用如WinSpy可监视计算机运行的所有窗口和模块。处理建议：在不影响正常业务的情况下，建议增加策略或者设置防火墙拦截异常访问。 135 Epmap服务，用于远程打开主机的telnet服务 ,易被入侵，也可获取更多关于远程主机的信息。处理建议：在不影响正常业务的情况下建议关闭或者增加访问策略。 139\",\"emphasized_text_contents\":[\"端口\",\"列表\",\"端口说明\"],\"languages\":[\"zho\"],\"parent_id\":\"2bfd3946197847a53faa1f16bb325d02\",\"element_id\":\"db491a676d3d62261b261b0421e2166d\",\"text_as_html\":\"<table>\\n<thead>\\n<tr><th style=\\\"text-align: right;\\\">      端口\\n列表</th><th>端口说明                                                                                                                                                                                                              </th></tr>\\n</thead>\\n<tbody>\\n<tr><td style=\\\"text-align: right;\\\">   21</td><td>ftp默认端口号，利用FTP服务因配置不当可能存在弱口令破解，或被木马利。处理建议：在不影响正常业务的情况下，建议关闭对外开放或者防止匿名登录。                                                                            </td></tr>\\n<tr><td style=\\\"text-align: right;\\\">   22</td><td>ssh默认端口号，此端口开放容易被爆破，弱口令进入系统。处理建议：在不影响正常业务的情况下，建议限制登录方式或采取强密码策略。                                                                                           </td></tr>\\n<tr><td style=\\\"text-align: right;\\\">   23</td><td>Telnet默认端口号，利用Telnet服务，可搜索远程登录Unix服务，扫描操作系统类型。存在提升权限、拒绝服务等漏洞，可使远程服务器崩溃。处理建议：在不影响正常业务的情况下建议关闭或者增加访问策略。                            </td></tr>\\n<tr><td style=\\\"text-align: right;\\\">   25</td><td>利用25端口，可寻找SMTP服务器，转发垃圾邮件。被多数木马程序利用如WinSpy可监视计算机运行的所有窗口和模块。处理建议：在不影响正常业务的情况下，建议增加策略或者设置防火墙拦截异常访问。                                  </td></tr>\\n<tr><td style=\\\"text-align: right;\\\">  135</td><td>Epmap服务，用于远程打开主机的telnet服务 ,易被入侵，也可获取更多关于远程主机的信息。处理建议：在不影响正常业务的情况下建议关闭或者增加访问策略。                                                                       </td></tr>\\n<tr><td style=\\\"text-align: right;\\\">  139</td><td>netbios-ssn服务，此端口可以提供windows文件、打印机共享和SAMBA服务，可被黑客利用获取主机用户名密码。处理建议：在不影响正常业务的情况下，建议关闭或者增加安全策略。                                                     </td></tr>\\n<tr><td style=\\\"text-align: right;\\\">  161</td><td>Snmp弱口令导致public泄漏。处理建议：在不影响正常业务的情况下，建议限制登录方式或采取强密码策略。                                                                                                                      </td></tr>\\n<tr><td style=\\\"text-align: right;\\\">  445</td><td>Microsoft-DS，为共享开放，可能被震荡波病毒利用；在局域网中可访问各种共享文件夹或共享打印机，黑客可通过该端口共享内部硬盘，甚至会悄无声息中将硬盘格式化。处理建议：在不影响正常业务的情况下，建议关闭或者增加安全策略。</td></tr>\\n<tr><td style=\\\"text-align: right;\\\"> 1433</td><td>用于供SQL Server对外提供服务，可能存在弱口令、提权等漏洞，导致入侵服务器。处理建议：在不影响正常业务的情况下，建议增加安全访问策略。                                                                                  </td></tr>\\n<tr><td style=\\\"text-align: right;\\\"> 1434</td><td>用于向请求者返回SQL Server使用了哪个TCP/IP端口，可能存在弱口令、提权等漏洞，导致入侵服务器。处理建议：在不影响正常业务的情况下，建议增加安全访问策略。                                                                </td></tr>\\n<tr><td style=\\\"text-align: right;\\\"> 1521</td><td>Oracle 可能存在账户弱口令漏洞，以及服务器溢出漏洞。处理建议：在不影响正常业务的情况下，建议增加安全访问策略。                                                                                                         </td></tr>\\n<tr><td style=\\\"text-align: right;\\\"> 3306</td><td>MySQL存在任意密码登陆漏洞，详情参考： CVE-2012-2122；可能存在账户弱口令漏洞，容易被爆破。处理建议：在不影响正常业务的情况下，建议增加安全访问策略。                                                                   </td></tr>\\n<tr><td style=\\\"text-align: right;\\\"> 3389</td><td>WIN2003用&quot;远程桌面&quot;等连接工具来连接到远程的服务器，可能存在账户弱口令、或者 CVE-2019-0708 远程桌面漏洞复现等问题，容易被爆破。处理建议：在不影响正常业务的情况下，建议增加安全访问策略。                    </td></tr>\\n<tr><td style=\\\"text-align: right;\\\"> 5432</td><td>PostgreSQL默认端口号，可能存在远程代码执行（CVE-2019-1058）、权限提升（CVE-2016-0766）、安全限制绕过（CVE-2015-0244）等漏洞。处理建议：在不影响正常业务的情况下，建议增加安全访问策略。                               </td></tr>\\n<tr><td style=\\\"text-align: right;\\\"> 5984</td><td>CouchDB端口，可能存在 CouchDB未授权访问漏洞。处理建议：在不影响正常业务的情况下，建议增加安全访问策略。                                                                                                               </td></tr>\\n<tr><td style=\\\"text-align: right;\\\"> 6379</td><td>Redis 默认端口号，Redis可能导致未授权访问或通过SSH登录服务器，导致服务器权限被获取和数据删除、泄露或加密勒索事件。处理建议：在不影响正常业务的情况下，建议增加安全访问策略。                                          </td></tr>\\n<tr><td style=\\\"text-align: right;\\\"> 7001</td><td>Weblogic端口，Weblogic控制台存在账户弱口令漏洞，Weblogic反序列漏洞。处理建议：在不影响正常业务的情况下，建议增加安全访问策略。                                                                                        </td></tr>\\n<tr><td style=\\\"text-align: right;\\\"> 9001</td><td>Supervisord，可能存在Supervisord远程命令执行漏洞(CVE-2017-11610)。处理建议：在不影响正常业务的情况下，建议增加安全访问策略。                                                                                          </td></tr>\\n<tr><td style=\\\"text-align: right;\\\"> 9200</td><td>作为Http协议，主要用于外部通讯, 一般都是给ElasticSearch-Head等工具连接ElasticSearch使用的，可能存在ElasticSearch 远程代码执行漏洞（CVE-2015-1427）。处理建议：在不影响正常业务的情况下，建议增加安全访问策略。        </td></tr>\\n<tr><td style=\\\"text-align: right;\\\">11211</td><td>Memcached监听端口，可能存在 Memcached未授权访问漏洞。处理建议：在不影响正常业务的情况下，建议增加安全访问策略。                                                                                                       </td></tr>\\n<tr><td style=\\\"text-align: right;\\\">27017</td><td>Memcached监听端口，可能存在 Memcached未授权访问漏洞。处理建议：在不影响正常业务的情况下，建议增加安全访问策略。                                                                                                       </td></tr>\\n<tr><td style=\\\"text-align: right;\\\">50000</td><td>SAP Management Console服务端口，可能存在 运程命令执行漏洞。处理建议：在不影响正常业务的情况下，建议增加安全访问策略。                                                                                                 </td></tr>\\n</tbody>\\n</table>\",\"titles\":\"#定义：网络中开放的与安全相关的端口，这些端口或极易被黑客利用，或能直接导致安全漏洞。\",\"type\":\"Table\"},\"page_content\":\"#定义：网络中开放的与安全相关的端口，这些端口或极易被黑客利用，或能直接导致安全漏洞。-端口 列表 端口说明 21 ftp默认端口号，利用FTP服务因配置不当可能存在弱口令破解，或被木马利。处理建议：在不影响正常业务的情况下，建议关闭对外开放或者防止匿名登录。 22 ssh默认端口号，此端口开放容易被爆破，弱口令进入系统。处理建议：在不影响正常业务的情况下，建议限制登录方式或采取强密码策略。 23 Telnet默认端口号，利用Telnet服务，可搜索远程登录Unix服务，扫描操作系统类型。存在提升权限、拒绝服务等漏洞，可使远程服务器崩溃。处理建议：在不影响正常业务的情况下建议关闭或者增加访问策略。 25 利用25端口，可寻找SMTP服务器，转发垃圾邮件。被多数木马程序利用如WinSpy可监视计算机运行的所有窗口和模块。处理建议：在不影响正常业务的情况下，建议增加策略或者设置防火墙拦截异常访问。 135 Epmap服务，用于远程打开主机的telnet服务 ,易被入侵，也可获取更多关于远程主机的信息。处理建议：在不影响正常业务的情况下建议关闭或者增加访问策略。 139\"}"
        #         }
        #     ],
        #     "query": "tcp的优点"
        # }
        
        # TODO 是否为json
        raw_output = response_data
        raw_output_dict = raw_output
        
        # 获取top_n检索结果
        knowledge_call_response_data = KnowledgeCallResponse(**raw_output_dict)
        retrieval_results = knowledge_call_response_data.retrieval_results
        top_n_retrieval_results = get_top_n_retrieval_results(retrieval_results=retrieval_results, n=maximum_number_of_recalls)
        
        # top_n检索结果转为知识节点默认输出schema
        output_list = []
        for retrieval_result in top_n_retrieval_results:
            if retrieval_result.source == RetrievalResultSourceType.DOC.value:
                output = json.loads(retrieval_result.content).get("page_content", "")   # 文档问答结果需要二次提取
            elif retrieval_result.source == RetrievalResultSourceType.DATA.value:
                output = retrieval_result.content
            output_list.append(KnowledgeNodeDefaultOutput(output=output))
    
        knowledge_node_default_outputs = KnowledgeNodeDefaultOutputs(output_list=output_list)
        
        # 解析响应数据
        parsed_output_dict = knowledge_node_default_outputs.model_dump(by_alias=True)
        parsed_output_json_str = json.dumps(parsed_output_dict, ensure_ascii=False)
        knowledge_node_data.output = parsed_output_json_str
        
        # 计算token消耗
        input_tokens = compute_tokens_by_transformers(text=parsed_input_json_str)
        output_tokens = compute_tokens_by_transformers(text=parsed_output_json_str)
        total_tokens = input_tokens + output_tokens
        token_and_cost = TokenAndCost(
            input_tokens=format_tokens(input_tokens),
            output_tokens=format_tokens(output_tokens),
            total_tokens=format_tokens(total_tokens)
        )
        knowledge_node_data.token_and_cost = token_and_cost
        
        node_status = "SUCCESS"
    except Exception as e:
        node_status = "FAILED"
        error_info = str(e)
        knowledge_node_data.error_info = error_info
        
    # 更新状态
    knowledge_node_data.node_status = node_status
    
    # 计算节点运行时间
    end_time = time.time()
    node_exe_cost = f"{round((end_time - start_time), 3)}s"
    knowledge_node_data.node_exe_cost = node_exe_cost
    
    # 数据库同步节点状态
    on_end(
        workflow_id=workflow_id,
        node_data=knowledge_node_data
    )
    
    knowledge_node_response = KnowledgeNodeResponse(node_data=knowledge_node_data)
    
    next_response = {"prenode_inputs": prenode_inputs}
    next_response.update(knowledge_node_response.model_dump())
    return next_response

def process_end_node(
    prenode_inputs: List[Dict],
    end_node_schema: EndNode
):
    start_time = time.time()
    
    # 校验node schema
    end_node_schema = EndNode(**end_node_schema)
    
    # 初始化节点状态
    end_node_data = NodeData(
        node_type=NodeType.END.value,
        node_status="RUNNING",
    )
    
    # 格式化前置节点输入数据
    all_nodes_data = format_prenodes_data(prenode_inputs=prenode_inputs)
    
    try:
        end_node_data.node_id = end_node_schema.node_id
        end_node_data.node_name = end_node_schema.node_name
        workflow_id = end_node_schema.flow_id
        
        # 数据库同步节点状态
        on_start(
            workflow_id=workflow_id,
            node_data=end_node_data
        )
        
        # 解析输入schema
        parsed_input_dict = format_input_schemas_to_dict(
            input_schema=end_node_schema.input_schema,
            prenode_results=all_nodes_data
        )
        if not parsed_input_dict:
            parsed_input_json_str = ""
        else:
            parsed_input_json_str = json.dumps(parsed_input_dict, ensure_ascii=False)
        end_node_data.input = parsed_input_json_str
        
        # End节点解析完称的输入等价于输出
        parsed_output_json_str = parsed_input_json_str
        end_node_data.output = parsed_output_json_str
        
        # 计算token消耗
        input_tokens = compute_tokens_by_transformers(text=parsed_input_json_str)
        output_tokens = compute_tokens_by_transformers(text=parsed_output_json_str)
        total_tokens = input_tokens + output_tokens
        token_and_cost = TokenAndCost(
            input_tokens=format_tokens(input_tokens),
            output_tokens=format_tokens(output_tokens),
            total_tokens=format_tokens(total_tokens)
        )
        end_node_data.token_and_cost = token_and_cost
        
        node_status = "SUCCESS"
    except Exception as e:
        node_status = "FAILED"
        error_info = str(e)
        end_node_data.error_info = error_info
        
    # 更新状态
    end_node_data.node_status = node_status
    
    # 计算节点运行时间
    end_time = time.time()
    node_exe_cost = f"{round((end_time - start_time), 3)}s"
    end_node_data.node_exe_cost = node_exe_cost
    
    # 数据库同步节点状态
    on_end(
        workflow_id=workflow_id,
        node_data=end_node_data
    )
    
    all_nodes_data.append(end_node_data)
    return EndNodeResponse(
        node_data=end_node_data,
        all_nodes_data=all_nodes_data
    ).model_dump()


async def aprocess_workflow_node(
        prenode_inputs: List[Dict],
        workflow_node_schema: WorkflowNode
):
    start_time = time.time()

    # 校验node schema
    workflow_node_schema = WorkflowNode(**workflow_node_schema)

    # 初始化节点状态
    workflow_node_data = NodeData(
        node_type=NodeType.COMPONENT.value,
        node_status="RUNNING",
    )
    try:
        workflow_node_data.node_id = workflow_node_schema.node_id
        workflow_node_data.node_name = workflow_node_schema.node_name
        workflow_id = workflow_node_schema.flow_id

        # 数据库同步节点状态
        on_start(
            workflow_id=workflow_id,
            node_data=workflow_node_data
        )

        # 格式化前置节点输入数据
        all_nodes_data = format_prenodes_data(prenode_inputs=prenode_inputs)
        # 解析输入schema
        parsed_input_dict = format_input_schemas_to_dict(
            input_schema=workflow_node_schema.input_schema,
            prenode_results=all_nodes_data
        )
        if not parsed_input_dict:
            parsed_input_json_str = ""
        else:
            parsed_input_json_str = json.dumps(parsed_input_dict, ensure_ascii=False)
        workflow_node_data.input = parsed_input_json_str

        sub_workflow_ids = workflow_node_data.sub_workflow_ids
        tenant_id = workflow_node_schema.tenant_id

        headers = {"tenant-id": tenant_id}
        body = {
            "requestBody": parsed_input_json_str
        }
        # TODO 节点功能实现
        sub_workflow_results = []
        for sub_workflow_id in sub_workflow_ids:
            body.update({"sub_workflowId": sub_workflow_id})
            if not (workflow_call_url := os.getenv("WORKFLOW_CALL_URL")):
                workflow_call_url = WORKFLOW_CALL_URL  # 向后兼容

            try:
                async with httpx.AsyncClient() as client:
                    workflow_call_response = await client.post(url=workflow_call_url, headers=headers, json=body, timeout=15)

                    if workflow_call_response.is_success:
                        sub_workflow_results.append({sub_workflow_id: workflow_call_response.json()})
                    else:
                        raise ValueError(f"子工作流调用响应状态异常, 状态码: {workflow_call_response.status_code}")
            except httpx.TimeoutException:
                raise ValueError("子工作流调用请求超时")
            except httpx.HTTPStatusError as e:
                raise ValueError(f"子工作流用请求状态异常, 状态码: {e.response.status_code}") from e
            except:
                raise

        raw_output = sub_workflow_results[0].get(sub_workflow_ids[0], "")
        parsed_output_json_str = json.dumps(raw_output, ensure_ascii=False)
        workflow_node_data.output = parsed_output_json_str

        # 计算token消耗
        input_tokens = compute_tokens_by_transformers(text=parsed_input_json_str)
        output_tokens = compute_tokens_by_transformers(text=parsed_output_json_str)
        total_tokens = input_tokens + output_tokens
        token_and_cost = TokenAndCost(
            input_tokens=format_tokens(input_tokens),
            output_tokens=format_tokens(output_tokens),
            total_tokens=format_tokens(total_tokens)
        )
        workflow_node_data.token_and_cost = token_and_cost

        node_status = "SUCCESS"
    except Exception as e:
        node_status = "FAILED"
        error_info = str(e)
        workflow_node_data.error_info = error_info

    # 更新状态
    workflow_node_data.node_status = node_status

    # 计算节点运行时间
    end_time = time.time()
    node_exe_cost = f"{round((end_time - start_time), 3)}s"
    workflow_node_data.node_exe_cost = node_exe_cost

    # 数据库同步节点状态
    on_end(
        workflow_id=workflow_id,
        node_data=workflow_node_data
    )

    workflow_node_response = WorkflowResponse(node_data=workflow_node_data)

    next_response = {"prenode_inputs": prenode_inputs}
    next_response.update(workflow_node_response.model_dump())

    return next_response