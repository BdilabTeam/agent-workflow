import json
from typing import List
from pydantic import BaseModel, Field, parse_obj_as

from langchain_core.tools import ToolException, StructuredTool
from langflow import CustomComponent
from langflow.field_typing import Data, Tool
from langflow.custom_schemas.agents import WorkflowNode, InputSchema, Schema, WorkflowSchema
import requests
from utils.constants import WORKFLOW_CALL_URL_AGENT
from utils.utils import create_input_schema


class AgentWorkflow(CustomComponent):
    display_name = "智能体工作流节点"

    def build_config(self):
        return {
            "workflow_node": {
                "display_name": "工作流节点schema",
                "required": False,
                "field_type": "dict"
            }
        }

    def build(self, workflow_node: WorkflowNode) -> Tool:
        tools = []

        if workflow_node != None:

            def _handle_error(error: ToolException) -> str:
                return (
                        "The following errors occurred during tool execution:"
                        + error.args[0]
                        + "Please try another tool."
                )

            try:
                # 工具集
                workflow_node = WorkflowNode(**workflow_node)
                workflow_schemas = workflow_node.workflow_schemas
                i = 0

                for workflow_schema in workflow_schemas:
                    i = i + 1
                    id = workflow_schema.workflow_id
                    name = workflow_schema.workflow_name
                    desc = workflow_schema.workflow_desc
                    input_schemas = workflow_schema.input_schema

                    # 动态创建输入schema
                    fields = [(input_schema.name, input_schema.type, input_schema.desc) for input_schema in
                              input_schemas]
                    DynamicInputSchema = create_input_schema(fields, i)

                    args = ",".join([f"{input_schema.name}: {input_schema.type}" for input_schema in input_schemas])
                    # func_body = "\n".join(
                    #     [f"    print(f'Argument {arg['name']} ({arg['type']}):', {arg['name']})" for arg in input_schemas])

                    function_string = f"""
def workflow_{i}({args}):
    import json
    import requests
    url = {WORKFLOW_CALL_URL_AGENT}
    headers = {{
        'tenant-id': '1',
        'Content-Type': 'application/json'
    }}
    request_body = {{ {', '.join(f"'{input_schema.name}': {input_schema.name}" for input_schema in input_schemas) } }}
    payload = {{
        'workflowId': '{id}',
        'input': request_body
    }}
    try:
        response = requests.post(url, headers=headers, json=payload)
        if 200 <= response.status_code < 300:
            response_json = response.json()
            if response_json.get('code') == 0:
                data = json.dumps(response_json.get('data').get('workflowResult'))
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
                    try:
                        local_namespace = {}
                        exec(function_string, globals(), local_namespace)
                    except Exception as e:
                        raise BaseException

                    structuredTool = StructuredTool.from_function(
                        func=local_namespace[f"workflow_{i}"],
                        name=name,
                        args_schema=DynamicInputSchema,
                        description=desc,
                        handle_tool_error=_handle_error,
                    )

                    tools.append(structuredTool)

            except Exception as e:
                pass
        return tools
