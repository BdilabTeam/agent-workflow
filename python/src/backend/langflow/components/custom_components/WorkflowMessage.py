from langflow import CustomComponent
from langflow.components.custom_components.schemas.workflow import MessageNode
from langflow.components.custom_components.utils.workflow_node_utils import process_message_node
from typing import List, Dict, Union

class Message(CustomComponent):
    id = "8"
    display_name = "工作流-消息"
    description = "Message Node"

    def build_config(self):
        return {
            "prenode_inputs": {
                "display_name": "前置节点输入",
                "required": False,
            },
            "message_node_schema": {
                "display_name": "消息节点schemas",
                "required": False,
                "field_type": "dict"
            }
        }

    def build(
        self,
        prenode_inputs: List[Dict] = [],
        message_node_schema: MessageNode = None
    ) -> Union[dict, Dict]:
        # message_node_schema = {
        #     "flow_id": "1",
        #     "node_id": "MessageID",
        #     "input_schema": {
        #         "inputParameters": [
        #             {
        #                 "name": "placeholder",
        #                 "input": {
        #                     "type": "string",
        #                     "schema": None,
        #                     "value": {
        #                         "type": "ref",
        #                         "content": {
        #                             "source_id": "StartID",
        #                             "name": "query"
        #                         }
        #                     }
        #                 }
        #             },
        #             {
        #                 "name": "new_list",
        #                 "input": {
        #                     "type": "list",
        #                     "schema": None,
        #                     "value": {
        #                         "type": "literal",
        #                         "content": "[1, 2]"
        #                     }
        #                 }
        #             }
        #         ]
        #     },
        #     "answer_content": "我需要输出{new_list[0]}和{placeholder}。"
        # }
        return process_message_node(prenode_inputs=prenode_inputs, message_node_schema=message_node_schema)