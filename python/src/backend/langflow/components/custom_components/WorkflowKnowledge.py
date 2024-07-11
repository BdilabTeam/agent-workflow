from typing import List, Dict, Union

from langflow import CustomComponent
# from .schemas import KnowledgeNode, KnowledgeNodeResponse, NodeData, TokenAndCost
# from .utils import (
#     format_prenodes_data, format_input_schemas_to_dict,
#     NodeType
# )

from langflow.components.custom_components.schemas.workflow import KnowledgeNode
from langflow.components.custom_components.utils import process_knowledge_node

class Knowledge(CustomComponent):
    id = "4"
    display_name = "工作流-知识"
    description = "Knowledge Node"
    
    def build_config(self):
        return {
            "prenode_inputs": {
                "display_name": "前置节点输入",
                "required": False,
            },
            
            "knowledge_node_schema": {
                "display_name": "知识节点schemas",
                "required": False,
                "field_type": "dict"
            }
        }

    async def build(
        self, 
        prenode_inputs: List[Dict] = [],
        knowledge_node_schema: KnowledgeNode = None
    ) -> Union[dict, Dict]:
        # knowledge_node_schema = {
        #     "tenant_id": 1,
        #     "flow_id": "1",
        #     "node_id": "KnowledgeID",
        #     "knowledge_ids": [
        #         "d728b8d382914250a634bf4aa0134d0d"
        #     ],
        #     "knowledge_schema": {
        #         "knowledge_name": "",
        #         "knowledge_config": {
        #             "search_strategy": "semantic",
        #             "maximum_number_of_recalls": 2,
        #             "minimum_matching_degree": 0.5
        #         }
        #     },
        #     "input_schema": {
        #         "inputParameters": [
        #             {
        #                 "name": "query",
        #                 "input": {
        #                     "type": "string",
        #                     "schema": None,
        #                     "value": {
        #                         "type": "literal",
        #                         "content": "事件研判规则有哪些？"
        #                     }
        #                 }
        #             }
        #         ]
        #     }
        # }
        return await process_knowledge_node(prenode_inputs=prenode_inputs, knowledge_node_schema=knowledge_node_schema)