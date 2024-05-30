from typing import List, Any
from pydantic import BaseModel, Field, parse_obj_as
from langchain_core.tools import ToolException, StructuredTool
from langflow import CustomComponent
from langflow.field_typing import Data, Tool
from langchain.agents import tool
from langchain_core.tools import Tool
from langflow.custom_schemas.agents import ToolNode, InputSchema, Schema, ToolSchema
import requests
from utils.constants import TOOL_CALL_URL_AGENT
from utils.utils import create_input_schema

class AgentTool(CustomComponent):
    display_name = "智能体工具节点"

    def build_config(self):
        return {
            "tool_node": {
                "display_name": "工具节点schema",
                "required": False,
                "field_type": "dict"
            }
        }

    def build(self, tool_node: ToolNode) -> Tool:
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

                    #动态创建输入schema
                    fields = [(input_schema.name, input_schema.type, input_schema.desc) for input_schema in input_schemas]
                    DynamicInputSchema = create_input_schema(fields, i)

                    args = ",".join([f"{input_schema.name}: {input_schema.type}" for input_schema in input_schemas])
                    # func_body = "\n".join(
                    #     [f"    print(f'Argument {arg['name']} ({arg['type']}):', {arg['name']})" for arg in input_schemas])

                    function_string = f"""
def tool_{i}({args}):
    import json
    import requests
    url = {TOOL_CALL_URL_AGENT}
    headers = {{
        'tenant-id': '1',
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
            if  response_json.get('code') == 0:
                data = json.dumps(response_json.get('data'), ensure_ascii=False)
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
                        func=local_namespace[f"tool_{i}"],
                        name=name,
                        description=desc,
                        args_schema=DynamicInputSchema,
                        handle_tool_error=_handle_error,
                    )

                    tools.append(structuredTool)
            except Exception as e:
                pass

        return tools