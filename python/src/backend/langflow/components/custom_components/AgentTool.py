from langflow import CustomComponent
from langflow.field_typing import Tool
from langchain_core.tools import Tool
from langflow.components.custom_components.schemas.agents import ToolNode
from langflow.components.custom_components.utils.agent_node_utils import process_tool_node

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

    def build(self, tool_node: ToolNode = None) -> Tool:\
    
        # tool_node =  {
        #     "tool_schemas": [
        #       {
        #         "tool_id": "f92955f6-a945-44eb-9c8b-6484a146c0ef",
        #         "tenant_id": 1,
        #         "tool_desc": "查询ip信息",
        #         "tool_name": "ip_info",
        #         "input_schema": [
        #           {
        #             "name": "ipList",
        #             "type": "list"
        #           }
        #         ]
        #       },
        #       {
        #         "tool_id": "4631baae97ef4197a162522d75e97789",
        #         "tenant_id": "1",
        #         "tool_desc": "针对多种钓鱼攻击类型（如账号密码获取、身份信息窃取等）智能生成钓鱼邮件内容，提供定制化的攻击策略",
        #         "tool_name": "钓鱼邮件",
        #         "input_schema": []
        #       }
        #     ]
        # }
        return process_tool_node(tool_node)