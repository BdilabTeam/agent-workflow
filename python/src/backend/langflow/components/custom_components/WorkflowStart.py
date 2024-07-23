
from typing import List, Dict, Union

from langflow import CustomComponent
# from .schemas import StartNode, StartNodeResponse, NodeData, TokenAndCost
# from .utils import format_input_schemas_to_dict, NodeType
from langflow.components.custom_components.schemas.workflow import StartNode
from langflow.components.custom_components.utils import process_start_node

class Start(CustomComponent):
    id = "1"
    display_name = "工作流-开始"
    description = "Start Node"

    def build_config(self):
        return {
            "start_node_schema": {
                "display_name": "开始节点schemas",
                "required": False,
                "field_type": "dict"
            }
        }

    def build(
        self,
        start_node_schema: StartNode = None
    ) -> Union[dict, Dict]:
        # start_node_schema = {
        #     "flow_id": "1",
        #     "node_id": "StartID",
        #     "node_name": "StartName",
        #     "input_schema": {
        #         "inputParameters": [
        #             {
        #                 "name": "event",
        #                 "input": {
        #                     "type": "string",
        #                     "schema": None,
        #                     "value": {
        #                         "type": "literal",
        #                         "content": "分析安全事件"
        #                     }
        #                 }
        #             }
        #         ]
        #     }
        # }
        return process_start_node(start_node_schema=start_node_schema)