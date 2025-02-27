from langflow import CustomComponent
from langflow.field_typing import Tool
from langflow.components.custom_components.schemas.agents import WorkflowNode
from langflow.components.custom_components.utils.agent_node_utils import process_workflow_node

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

    def build(self, workflow_node: WorkflowNode = None) -> Tool:
        # workflow_node = {
        #   "workflow_schemas": [
        #     {
        #       "tenant_id": 1,
        #       "workflow_id": "a07d3b26d05f49d99cf26bf7454e56b7",
        #       "input_schema": [
        #         {
        #           "name": "name",
        #           "type": "str"
        #         }
        #       ],
        #       "workflow_desc": "查询对应名字的工作流",
        #       "workflow_name": "workflow1"
        #     }
        #   ]
        # }
        return process_workflow_node(workflow_node)
