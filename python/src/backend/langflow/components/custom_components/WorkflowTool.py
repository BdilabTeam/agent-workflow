from typing import List, Dict, Union

from langflow import CustomComponent

# from .schemas import ToolNode, ToolNodeResponse, NodeData, TokenAndCost
# from .utils import (
#     format_prenodes_data, 
#     format_input_schemas_to_dict, 
#     NodeType
# )
# from .rest import RESTClientObject, Configuration, RESTResponse

from langflow.components.custom_components.schemas.workflow import ToolNode
from langflow.components.custom_components.utils import process_tool_node

class Tool(CustomComponent):
    id = "5"
    display_name = "工作流-工具"
    description = "Tool Node"

    def build_config(self):
        return {
            "prenode_inputs": {
                "display_name": "前置节点输入",
                "required": False,
            },
            
            "tool_node_schema": {
                "display_name": "工具节点schemas",
                "required": False,
                "field_type": "dict"
            }
        }

    def build(
        self, 
        prenode_inputs: List[Dict] = [],
        tool_node_schema: ToolNode = None
    ) -> Union[dict, Dict]:
        # tool_node_schema = {
        #     "tenant_id": 1,
        #     "flow_id": "1",
        #     "node_id": "ToolID2",
        #     "tool_ids": [
        #         "f92955f6-a945-44eb-9c8b-6484a146c0ef"
        #     ],
        #     "input_schema": {
        #         "inputParameters": [
        #             {
        #                 "name": "ipList",
        #                 "input": {
        #                     "type": "list",
        #                     "schema": None,
        #                     "value": {
        #                         "type": "literal",
        #                         "content": "[\"15.197.130.221\"]"
        #                     }
        #                 }
        #             }
        #         ]
        #     }
        # }
        return process_tool_node(prenode_inputs=prenode_inputs, tool_node_schema=tool_node_schema)
      
