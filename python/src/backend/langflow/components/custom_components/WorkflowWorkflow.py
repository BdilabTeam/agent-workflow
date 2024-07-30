# from typing import List, Dict, Union
# from langflow import CustomComponent
# from langflow.components.custom_components.schemas.workflow import WorkflowNode
# from langflow.components.custom_components.utils.workflow_node_utils import aprocess_workflow_node
#
#
# class Workflow(CustomComponent):
#     id = "6"    # Unique ID
#     display_name = "工作流-工作流"
#     description = "Workflow Node"
#
#     def build_config(self):
#         return {
#             "prenode_inputs": {
#                 "display_name": "前置节点输入",
#                 "required": False,
#             },
#             "workflow_node_schema": {    # build方法参数名称
#                 "display_name": "工作流节点schemas",
#                 "advanced": False,
#                 "required": False,
#                 "field_type": "dict"
#             },
#         }
#
#     async def build(
#         self,
#         prenode_inputs: List[Dict] = [],
#         workflow_node_schema: WorkflowNode = None
#     ) -> Union[dict, Dict]:
#         # workflow_node_schema = {
#         #     "tenant_id": "1",
#         #     "flow_id": "1",
#         #     "node_id": "WorkflowID",
#         #     "node_name": "WorkflowName",
#         #     "sub_flow_ids": [
#         #         "a07d3b26d05f49d99cf26bf7454e56b7"
#         #     ],
#         #     "input_schema": {
#         #         "inputParameters": [
#         #             {
#         #                 "name": "ipList",
#         #                 "input": {
#         #                     "type": "list",
#         #                     "schema": None,
#         #                     "value": {
#         #                         "type": "literal",
#         #                         "content": "['15.197.130.221']"
#         #                     }
#         #                 }
#         #             }
#         #         ]
#         #     }
#         # }
#         return await aprocess_workflow_node(prenode_inputs=prenode_inputs, workflow_node_schema=workflow_node_schema)