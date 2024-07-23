from typing import List, Dict, Union

from langflow import CustomComponent

# from .schemas import LLMNode, LLMNodeResponse, NodeData, TokenAndCost
# from .utils import (
#     format_prenodes_data, 
#     format_input_schemas_to_dict,
#     format_output_schemas_to_dict,
#     safe_format_prompt,
#     NodeType
# )

from langflow.components.custom_components.schemas.workflow import LLMNode
from langflow.components.custom_components.utils import aprocess_llm_node

class LLM(CustomComponent):
    id = "3"
    display_name = "工作流-LLM"
    description = "LLM Node"

    def build_config(self):
        return {
            "prenode_inputs": {
                "display_name": "前置节点输入",
                "required": False,
            },
            "llm_node_schema": {
                "display_name": "LLM节点schemas",
                "advanced": False,
                "required": False,
                "field_type": "dict"
            },
        }

    async def build(
        self,
        prenode_inputs: List[Dict] = [],
        llm_node_schema: LLMNode = None
    ) -> Union[dict, Dict]:
        # llm_node_schema = {
        #     "flow_id": "1",
        #     "node_id": "LLMID",
        #     "node_name": "LLMName",
        #     "prompt": "分析ip详情: {{ip_info}}",
        #     "model_schema": {
        #         "model_name": "qwen1.5-14b-chat",
        #         "model_parameters": {
        #             "temperature": 0.5,
        #             "openai_api_key": "EMPTY",
        #             "openai_base_url": "http://172.18.22.19:7002/v1"
        #         },
        #         "model_quota": {
        #             "token_limit": 4096,
        #             "token_resp": 4000,
        #             "system_prompt_limit": 3700
        #         }
        #     },
        #     "input_schema": {
        #         "inputParameters": [
        #             {
        #                 "name": "ip_info",
        #                 "input": {
        #                     "type": "string",
        #                     "schema": None,
        #                     "value": {
        #                         "type": "ref",
        #                         "content": {
        #                             "source_id": "ToolID",
        #                             "name": "data"
        #                         }
        #                     }
        #                 }
        #             }
        #         ]
        #     },
        #     "output_schema": {
        #         "outputs": [
        #             {
        #                 "name": "llm_output",
        #                 "type": "string",
        #                 "schema": None
        #             }
        #         ]
        #     }
        # }
        return await aprocess_llm_node(prenode_inputs=prenode_inputs, llm_node_schema=llm_node_schema)