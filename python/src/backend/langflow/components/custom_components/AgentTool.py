from typing import List
from pydantic import BaseModel, Field, parse_obj_as
from langchain_core.tools import ToolException, StructuredTool
from langflow import CustomComponent
from langflow.field_typing import Data, Tool
from langchain.agents import tool
from langchain_core.tools import Tool
from langflow.custom_schemas.agents import ToolNode, InputSchema, Schema, ToolSchema
import requests


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

                    args = ",".join([f"{input_schema.name}: {input_schema.type}" for input_schema in input_schemas])
                    # func_body = "\n".join(
                    #     [f"    print(f'Argument {arg['name']} ({arg['type']}):', {arg['name']})" for arg in input_schemas])

                    function_string = f"""
def tool_{i}({args}):
    import json
    import requests
    url = "http://172.22.102.61:48080/admin-api/plugins/tool/external/call/test"
    headers = {{
        'tenant-id': '1',
        'Content-Type': 'application/json'
    }}
    request_body = json.dumps({{ {', '.join(f"'{input_schema.name}': {input_schema.name}" for input_schema in input_schemas)} }}, ensure_ascii=False)
    payload = {{
        'requestBody': request_body,
        'toolId': '{id}'
    }}
    response = requests.post(url, json=payload, headers=headers)
    response_json = response.json()
    data = json.dumps(response_json.get('data'), ensure_ascii=False)
    return data
    """

                    local_namespace = {}
                    exec(function_string, globals(), local_namespace)

                    structuredTool = StructuredTool.from_function(
                        func=local_namespace[f"tool_{i}"],
                        name=name,
                        description=desc,
                        handle_tool_error=_handle_error,
                    )
                    

                    tools.append(structuredTool)
            except Exception as e:
                pass

        return tools