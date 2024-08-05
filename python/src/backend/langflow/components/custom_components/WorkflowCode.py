from typing import List, Dict, Union
from langflow import CustomComponent

# from ..custom_components.schemas.workflow import CodeNode
# from ..custom_components.utils.workflow_node_utils import process_code_node

from langflow.components.custom_components.schemas.workflow import CodeNode
from langflow.components.custom_components.utils.workflow_node_utils import aprocess_code_node


class Code(CustomComponent):
    id = "6"  # Unique ID
    display_name = "工作流-代码节点"  # Langflow UI节点展示名称
    description = "Code Node"  # 节点描述

    def build_config(self):
        return {
            "prenode_inputs": {
                "display_name": "前置节点输入",
                "required": False,
            },
            "code_node_schema": {  # build方法参数名称
                "display_name": "代码节点schemas",  # Langflow UI入参展示名称
                "advanced": False,
                "required": False,
                "field_type": "dict"
            },
        }

    async def build(
        self,
        prenode_inputs: List[Dict] = [],
        code_node_schema: CodeNode = None  # 节点参数schema
    ) -> Union[dict, Dict]:
#         code_node_schema = {
#             "flow_id": "1",
#             "node_id": "CodeID",
#             "code": """
# def main(args: Args) -> Output:
#     params = args['params']
#     ret: Output = {
#         "key0": params['a'] + params['b'],
#         "key1": ["hello", "world"],
#         "key2": {
#             "key21": "hi"
#         },
#     }
#     return ret
#         """,
#             "input_schema": {
#                 "inputParameters": [
#                     {
#                         "name": "a",
#                         "input": {
#                             "type": "string",
#                             "schema": None,
#                             "value": {
#                                 "type": "literal",
#                                 "content": "5"
#                             }
#                         }
#                     },
#                     {
#                         "name": "b",
#                         "input": {
#                             "type": "string",
#                             "schema": None,
#                             "value": {
#                                 "type": "ref",
#                                 "content": {
#                                     "source_id": "StartID",
#                                     "name": "query"
#                                 }
#                             }
#                         }
#                     }
#                 ]
#             },
#             "output_schema": {
#                 "outputs": [
#                     {
#                         "name": "key0",
#                         "type": "string",
#                         "schema": None
#                     },
#                     {
#                         "name": "key1",
#                         "type": "list",
#                         "schema": None
#                     },
#                     {
#                         "name": "key2",
#                         "type": "dict",
#                         "schema": None
#                     }
#                 ]
#             }
#         }
        return await aprocess_code_node(
            prenode_inputs=prenode_inputs,
            code_node_schema=code_node_schema
        )  # utils.workflow_node_utils.py中实现节点
