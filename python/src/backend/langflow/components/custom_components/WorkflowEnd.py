from typing import List, Dict

from langflow import CustomComponent
from langflow.field_typing import Data

# from .schemas import EndNode, EndNodeResponse, NodeData, TokenAndCost
# from .utils import (
#     format_prenodes_data, 
#     format_input_schemas_to_dict,
#     NodeType,
#     compute_tokens_by_transformers,
#     format_tokens
# )

from langflow.components.custom_components.schemas.workflow import EndNode
from langflow.components.custom_components.utils import process_end_node

class End(CustomComponent):
    id = "2"
    display_name = "工作流-结束"
    description = "End Node"

    def build_config(self):
        return {
            "prenode_inputs": {
                "display_name": "前置节点原始输入",
                "required": False,
            },
            "end_node_schema": {
                "display_name": "结束节点schema",
                "required": False,
                "field_type": "dict"
            }
        }

    def build(
        self, 
        prenode_inputs: List[Dict] = [],
        end_node_schema: EndNode = None
    ) -> Data:
        # end_node_schema = {
        #     "flow_id": "1",
        #     "node_id": "EndID",
        #     "prompt": "Here is the {{variable}}",
        #     "input_schema": {
        #         "inputParameters": [
        #             {
        #                 "name": "ref_llm_output",
        #                 "input": {
        #                     "type": "string",
        #                     "schema": None,
        #                     "value": {
        #                         "type": "ref",
        #                         "content": {
        #                             "source_id": "LLMID",
        #                             "name": "llm_output"
        #                         }
        #                     }
        #                 }
        #             },
        #             {
        #                 "name": "摆脱push的方案",
        #                 "input": {
        #                     "type": "string",
        #                     "schema": None,
        #                     "value": {
        #                         "type": "ref",
        #                         "content": {
        #                             "source_id": "LLMID-2",
        #                             "name": "plan"
        #                         }
        #                     }
        #                 }
        #             }
        #         ]
        #     }
        return process_end_node(prenode_inputs=prenode_inputs, end_node_schema=end_node_schema)
        